import argparse

import requests
import time
import os

from dotenv import load_dotenv

from youtuber import download_tracks

load_dotenv()

ALBUM_URL_PREFIX = 'https://listenbrainz.org/album/'
PLAYLIST_URL_PREFIX = 'https://listenbrainz.org/playlist/'
TRACK_URL_PREFIX = 'https://listenbrainz.org/track/'

def rate_limits(period):
    def decorator(func):
        last_reset = time.time()

        def wrapper(*args, **kwargs):
            nonlocal last_reset

            # Calculate time elapsed since last reset
            elapsed = time.time() - last_reset

            # If elapsed time is greater than the period, reset the call count
            if elapsed > period:
                calls = 0
                last_reset = time.time()
            else:
                # sleep until period is reached
                time.sleep(period - elapsed)
                last_reset = time.time()

            # Call the original function
            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_listenbrainz_playlist_tracks(playlist_id):
    url = f"https://api.listenbrainz.org/1/playlist/{playlist_id}"
    resp = requests.get(url, headers={ 'Authorization': f'Token {os.environ.get("LISTENBRAINZ_TOKEN")}' })
    resp.raise_for_status()
    data = resp.json()
    # Adjust this according to the actual ListenBrainz API structure
    return [
        {'artist': t['creator'], 'title': t['title'], 'mbid': t['identifier'][0].split('/')[-1]}
        for t in data['playlist']['track']
    ]

def get_listenbrainz_album_tracks(album_id):
    url = f"https://musicbrainz.org/ws/2/release/{album_id}?fmt=json&inc=recordings"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # Adjust this according to the actual ListenBrainz API structure
    recordings = [ t['recording']['id'] for m in data['media'] for t in m['tracks'] ]
    return [ get_track_metadata(recording_id) for recording_id in recordings ]

@rate_limits(period=1)
def get_track_metadata(track_id):
    url = f"https://musicbrainz.org/ws/2/recording/{track_id}?fmt=json&inc=artists"
    print(f'Requesting musicbrainz {url}')
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # Adjust this according to the actual MusicBrainz API structure
    return { 'artist': data['artist-credit'][0]['name'], 'title': data['title'], 'mbid': track_id }

def main():
    parser = argparse.ArgumentParser(description='Convert ListenBrainz playlist to YouTube URLs.')
    parser.add_argument('playlist_id_or_url', metavar='PLAYLIST_ID_OR_URL', type=str, help='ListenBrainz playlist ID or URL')
    args = parser.parse_args()

    playlist_id = playlist_id_or_url = args.playlist_id_or_url
    if playlist_id_or_url.startswith(TRACK_URL_PREFIX):
        track_id = playlist_id_or_url[len(TRACK_URL_PREFIX):]
        if track_id.endswith('/'):
            track_id = track_id[:-1]
        tracks = [ get_track_metadata(track_id) ]
    elif playlist_id_or_url.startswith(PLAYLIST_URL_PREFIX):
        playlist_id = playlist_id_or_url[len(PLAYLIST_URL_PREFIX):]
        if playlist_id.endswith('/'):
            playlist_id = playlist_id[:-1]
        tracks = get_listenbrainz_playlist_tracks(playlist_id)
    elif playlist_id_or_url.startswith(ALBUM_URL_PREFIX):
        album_id = playlist_id_or_url[len(ALBUM_URL_PREFIX):]
        if album_id.endswith('/'):
            album_id = album_id[:-1]
        tracks = get_listenbrainz_album_tracks(album_id)


    download_tracks(tracks)

if __name__ == "__main__":
    main()
