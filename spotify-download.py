#!/usr/bin/python3
import sys
import argparse

from spotify_scraper import SpotifyClient

from youtuber import download_tracks

def main():
    parser = argparse.ArgumentParser(description='Convert Spotify URL to a downloaded MP3.')
    parser.add_argument('spotify_url', metavar='SPOTIFY_URL', type=str, help='The spotify link')
    args = parser.parse_args()

    spotify_url = args.spotify_url
    if spotify_url is None:
        sys.exit('Specify a URL')

    # Initialize the client
    client = SpotifyClient()

    # Get track information
    track_info = client.get_track_info(spotify_url)

    # Extract and print artist name and title
    artist_name = track_info['artists'][0]['name']
    track_title = track_info['name']
    release_year = track_info['release_date'].split('-')[0]

    print(f"Artist: {artist_name}")
    print(f"Title: {track_title}")
    print(f"Release Date: {release_year}")

    # When done, close the client
    client.close()
    download_tracks([ { 'title': track_title, 'artist': artist_name, 'release_year': release_year } ])

if __name__ == '__main__':
    main()
