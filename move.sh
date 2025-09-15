#!/bin/bash

TARGET=~/MusicS3/Random\ Pop

for file in *.mp3; do
	echo "'$file'"
	if [ -f "${TARGET}/$file" ]; then
		echo "\tFound!"
	else
		mv "$file" "${TARGET}/$file"
		cmus-remote "${TARGET}/$file"
	fi
done
