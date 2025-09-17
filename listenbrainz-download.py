import argparse

import requests

from youtuber import download_tracks

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
    parser.add_argument('playlist_id', metavar='PLAYLIST_ID', type=str, help='ListenBrainz playlist ID')
    args = parser.parse_args()

    playlist_id = args.playlist_id
    tracks = get_listenbrainz_playlist_tracks(playlist_id)
    download_tracks(tracks)

if __name__ == "__main__":
    main()
