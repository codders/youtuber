import os
import argparse
import traceback
from time import sleep
import shutil

import requests
from dotenv import load_dotenv

from googleapiclient.discovery import build

import yt_dlp

from ffmpeg import FFmpeg

from mutagen.id3 import ID3, TIT2, TPE1, TYER

load_dotenv()
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
TARGET_FOLDER = os.environ.get('TARGET_FOLDER')

def youtube_search(youtube, query):
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=1,
        type="video"
    )
    response = request.execute()
    items = response.get("items", [])
    if items:
        video_id = items[0]['id']['videoId']
        return f'https://www.youtube.com/watch?v={video_id}'
    return None

def download_audio(url, target):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'js_runtimes': { 'deno': { 'path': 'node_modules/deno/deno' } },
        'remote_components': [ 'ejs:github' ],
        'outtmpl': target
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download( [ url ] )
        if error_code != 0:
            print('Download error code %d' % error_code)

def get_release_year(mbid):
    sleep(1)
    url = f"https://musicbrainz.org/ws/2/recording/{mbid}?fmt=json"
    resp = requests.get(url, headers={'User-Agent': 'Youtuber CLI v0.1'})
    resp.raise_for_status()
    data = resp.json()
    return data['first-release-date'].split('-')[0]

def convert_to_mp3(input, target):
    try:
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(input)
            .option("vn")
            .output(target)
        )
        ffmpeg.execute()
        os.unlink(input)
    except Exception as e:
        print(f"Unable to convert video to mp3 for '{input}'")

def tag_mp3(filename, artist, title, release_year):
    audio = ID3(filename)
    if len(audio.getall("TIT2")) > 0:
        return
    audio.add(TIT2(encoding=3, text=title))
    audio.add(TPE1(encoding=3, text=artist))
    audio.add(TYER(encoding=3, text=release_year))
    audio.save(v2_version=3)
    print(f"Tagged {filename}")

def get_target_folder_filename(filename):
    return f"{TARGET_FOLDER}/{filename}"

def move_file_to_target_folder(filename):
    target = get_target_folder_filename(filename)
    if os.path.exists(target):
        print(f"{target} already exists... deleting source")
        os.unlink(filename)
        return None
    else:
        shutil.move(filename, target)
        return target

def add_to_cmus(filename):
    os.system(f"cmus-remote \"{filename}\"")
    print(filename)

def fs_safe(name):
    return name.replace('/', '_')

def download_tracks(tracks):
    print('')
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    for t in tracks:
        query = f"{t['artist']} {t['title']}"
        mp4_filename_root = f"{fs_safe(t['artist'])} - {fs_safe(t['title'])}"
        mp4_filename_full = f"{mp4_filename_root}.m4a"
        mp3_filename = f"{fs_safe(t['artist'])} - {fs_safe(t['title'])}.mp3"
        if os.path.exists(get_target_folder_filename(mp3_filename)):
            print(f'Already added {query} to mp3 collection ... skipping conversion')
            continue

        if os.path.exists(mp3_filename):
            print(f'Already converted {query} to mp3 ... skipping conversion')
        else:
            if os.path.exists(f"{mp4_filename_full}.m4a"):
                print(f"Already downloaded video for '{query}' ... skipping download")
            else:
                url = youtube_search(youtube, query)
                if url:
                    print(f"Found youtube video for '{query}' - {url}")
                    try:
                        download_audio(url, target=mp4_filename_root)
                    except Exception as e:
                        print(f"Unable to download video for '{query}'")
                        print(e)
                        print(traceback.format_exc())
                        if os.path.exists(mp4_filename_full):
                            os.unlink(mp4_filename_full)
                        continue
            convert_to_mp3(mp4_filename_full, mp3_filename)

        if os.path.exists(mp3_filename):
            if 'mbid' in t and not 'release_year' in t:
                t['release_year'] = get_release_year(t['mbid'])
            tag_mp3(mp3_filename, t['artist'], t['title'], t['release_year'])
            new_path = move_file_to_target_folder(mp3_filename)
            if new_path is not None:
                add_to_cmus(new_path)
