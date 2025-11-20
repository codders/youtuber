import argparse

import requests

from youtuber import download_tracks

PLAYLIST_URL_PREFIX = 'https://listenbrainz.org/playlist/'

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

def main():
    parser = argparse.ArgumentParser(description='Convert ListenBrainz playlist to YouTube URLs.')
    parser.add_argument('playlist_id_or_url', metavar='PLAYLIST_ID_OR_URL', type=str, help='ListenBrainz playlist ID or URL')
    args = parser.parse_args()

    playlist_id = playlist_id_or_url = args.playlist_id_or_url
    if playlist_id_or_url.startswith(PLAYLIST_URL_PREFIX):
        playlist_id = playlist_id_or_url[len(PLAYLIST_URL_PREFIX):]
        if playlist_id.endswith('/'):
            playlist_id = playlist_id[:-1]

    tracks = get_listenbrainz_playlist_tracks(playlist_id)
    download_tracks(tracks)

if __name__ == "__main__":
    main()
