import argparse

import requests
import time

from youtuber import download_audio, convert_to_mp3, tag_mp3, \
        move_file_to_target_folder, add_to_cmus

def main():
    parser = argparse.ArgumentParser(description='Convert ListenBrainz playlist to YouTube URLs.')
    parser.add_argument('youtube_url', metavar='YOUTUBE_URL', type=str, help='Youtube URL')
    parser.add_argument('artist', metavar='ARTIST', type=str, help='Artist Name')
    parser.add_argument('title', metavar='TITLE', type=str, help='Title')
    parser.add_argument('year', metavar='YEAR', type=str, help='Release Year')
    args = parser.parse_args()
    target = f"{args.artist} - {args.title}"
    target_m4a = f"{target}.m4a"
    target_mp3 = f"{target}.mp3"

    download_audio(args.youtube_url, target)
    convert_to_mp3(target_m4a, target_mp3)
    tag_mp3(target_mp3, args.artist, args.title, args.year)
    destination = move_file_to_target_folder(target_mp3)
    add_to_cmus(destination)

if __name__ == "__main__":
    main()
