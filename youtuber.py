import os
import argparse
import traceback
from time import sleep
import shutil

import requests
from dotenv import load_dotenv

from googleapiclient.discovery import build

from pytube import YouTube
from pytube.innertube import _default_clients

from ffmpeg import FFmpeg

from mutagen.id3 import ID3, TIT2, TPE1, TYER

load_dotenv()
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
TARGET_FOLDER = os.environ.get('TARGET_FOLDER')

def get_listenbrainz_playlist_tracks(playlist_id):
    url = f"https://api.listenbrainz.org/1/playlist/{playlist_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # Adjust this according to the actual ListenBrainz API structure
    return [
        {'artist': t['creator'], 'title': t['title'], 'mbid': t['identifier'][0].split('/')[-1]}
        for t in data['playlist']['track']
    ]

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

def download_video(url, target):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        output_video = yt.title.replace(" ", "_")
        output_video = "".join([c for c in output_video if c.isalnum() or c in "._- "])
        video_stream.download(filename=target)
    except:
        _default_clients["ANDROID_EMBED"] = _default_clients["MWEB"]
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        output_video = yt.title.replace(" ", "_")
        output_video = "".join([c for c in output_video if c.isalnum() or c in "._- "])
        video_stream.download(filename=target)

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

def tag_mp3(filename, artist, title, mbid):
    audio = ID3(filename)
    if len(audio.getall("TIT2")) > 0:
        return
    release_year = get_release_year(mbid)
    audio.add(TIT2(encoding=3, text=title))
    audio.add(TPE1(encoding=3, text=artist))
    audio.add(TYER(encoding=3, text=release_year))
    audio.save(v2_version=3)
    print(f"Tagged {filename}")

def move_file_to_target_folder(filename):
    target = f"{TARGET_FOLDER}/{filename}"
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

def main():
    parser = argparse.ArgumentParser(description='Convert ListenBrainz playlist to YouTube URLs.')
    parser.add_argument('playlist_id', metavar='PLAYLIST_ID', type=str, help='ListenBrainz playlist ID')
    args = parser.parse_args()

    playlist_id = args.playlist_id
    tracks = get_listenbrainz_playlist_tracks(playlist_id)
    print('')
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    for t in tracks:
        query = f"{t['artist']} {t['title']}"
        mp4_filename = f"{t['artist']} - {t['title']}.mp4"
        mp3_filename = f"{t['artist']} - {t['title']}.mp3"
        if os.path.exists(mp3_filename):
            print(f'Already converted {query} to mp3 ... skipping conversion')
        else:
            if os.path.exists(mp4_filename):
                print(f"Already downloaded video for '{query}' ... skipping download")
            else:
                url = youtube_search(youtube, query)
                if url:
                    print(f"Found youtube video for '{query}' - {url}")
                    try:
                        download_video(url, target=mp4_filename)
                    except Exception as e:
                        print(f"Unable to download video for '{query}'")
                        print(e)
                        print(traceback.format_exc())
                        if os.path.exists(mp4_filename):
                            os.unlink(mp4_filename)
                        continue
            convert_to_mp3(mp4_filename, mp3_filename)
        if os.path.exists(mp3_filename):
            tag_mp3(mp3_filename, t['artist'], t['title'], t['mbid'])
            new_path = move_file_to_target_folder(mp3_filename)
            if new_path is not None:
                add_to_cmus(new_path)

if __name__ == "__main__":
    main()
