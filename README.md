# Untitled.stream + Samply Downloader

A very fast ai generated python script to batch download untitled and samply projects.

## How it works
The script reads links.txt, extracts valid urls:
`https://untitled.stream/library/project/...`
`https://samply.app/p/...`

For each project, it creates a folder with the project name and author name and then downloads the tracks in that folder in this format:
`Downloads/{Project Name}, {Creator Name}/{Track Name}.mp3`

The script also converts all audio files into mp3s unless they are over 10mb or have a .flac extension.


## Usage
1. Download repository as zip
2. Unzip and open links.txt
2. Paste untitled.stream and samply links into links.txt
3. Run ```python3 untitled_downloader.py``` in Terminal
4. When the script is done the audio files will be available in untitled_downloader_main/Downloads


### Requirements
`ffmpeg` (To convert file into MP3)

### Samply link requirements
```pip install playwright``` (headless browser automation)
```playwright install chromium```


## Other
I've also included convert_covers.py that I used to convert the files in untitled_downloader/Cover art into pngs, and merge_ye_albums.py to delete duplicate ye songs. I recommend handing merge_ye_albums.py to Claude code and letting it use it to remove lower quality duplicate songs.

Credits to enmilyisoffline and icefields for scraping functionality.
