# youtuber

Some scripts for downloading music from youtube.

## Background

Downloading music from Youtube is a bit of a cat-and-mouse game. I've tried a few
different projects - [spotdl](https://github.com/spotDL/spotify-downloader),
[pytube](https://github.com/pytube/pytube), [pytube2](https://github.com/Josh-XT/pytube2).
They seemed to work for a while, but I hit dead-ends with each of them over the course of
2025.

The current leading solution seems to be [yt-dlp](https://github.com/yt-dlp/yt-dlp) - it
seems well-maintained and goes quite deep solving the problem. Since I moved away from
spotdl, I managed to cut Spotify completely out of my music listening flow. Now it's just
[listenbrainz](https://listenbrainz.org), [cmus](https://cmus.github.io/),
[cmus status scrobbler](https://github.com/vjeranc/cmus-status-scrobbler) and this downloader.

## Installation

Clone the project and install the dependencies in the Pipfile and the package.json:

```
npm install
pipenv install
pipenv shell
```

## Usage

The project needs to know where to put the downloaded MP3s, and it needs a youtube
search API key. You can supply these in the environment, or a `.env` file:

```
YOUTUBE_API_KEY=<YOUR YOUTUBE SEARCH API KEY>
TARGET_FOLDER=/some/absolute/path
```

If you're downloading from Listenbrainz, you can simply:

```
python listenbrainz-download.py https://listenbrainz.org/playlist/PLAYLIST_ID/
```
