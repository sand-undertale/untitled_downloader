# Untitled.stream + Samply Downloader

A tool to batch-download tracks from [untitled.stream](https://untitled.stream) and [samply.app](https://samply.app) project links, in the audio format of your choice (MP3, ALAC, WAV, FLAC, AAC, OGG, or Opus).

Comes in two flavors:
- **The App** — a point-and-click window. No terminal, no editing text files. Recommended for most people.
- **The command-line script** — for anyone who prefers running it from Terminal/Command Prompt.

---

## 1. Requirements

You need these installed once, before first use:

| Requirement | Why | Install |
|---|---|---|
| **Python 3** | Runs the app/script | Mac/Linux usually have it. Windows: [python.org/downloads](https://www.python.org/downloads/) (check "Add Python to PATH" during install) |
| **ffmpeg** | Converts audio to your chosen format | Mac: `brew install ffmpeg` · Windows: [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) (add the `bin` folder to your PATH) · Linux: `sudo apt install ffmpeg` |
| **Playwright** *(only for Samply links)* | Automates loading the Samply page to find track files | Installed for you with one click inside the app (see below), or manually: `pip install playwright && playwright install chromium` |

To check if something is already installed, open Terminal/Command Prompt and run `python3 --version` and `ffmpeg -version`. If either says "command not found," install it first.

---

## 2. Using the App (recommended)

1. Unzip the downloaded folder.
2. Double-click to launch:
   - **macOS/Linux:** `Run App (Mac_Linux).command`
     - First launch on Mac may show a security warning since the file isn't from the App Store. Right-click the file → **Open** → **Open** again to confirm. You only need to do this once.
   - **Windows:** `Run App (Windows).bat`
     - Windows SmartScreen may warn about an unrecognized app. Click **More info** → **Run anyway**.
3. A window opens with:
   - A big text box — paste your untitled.stream / samply.app links here, one per line (or several on the same line, the app will find them).
   - A **format dropdown** — pick `mp3`, `alac`, `wav`, `flac`, `aac`, `ogg`, or `opus`.
   - A **Download** button.
   - An **Install Samply support (Playwright)** button — click this once the first time you plan to download Samply links. It only needs to run once ever.
   - An **Open Downloads Folder** button — jumps straight to your finished files once downloading is done.
   - A live **log** panel showing progress for every track.
4. Click **Download** and watch the log. When it says `ALL DONE!`, click **Open Downloads Folder**.

Your files land in a `Downloads` folder next to the app, organized like:
```
Downloads/
  Song Title, Artist Name/
    Track 1.mp3
    Track 2.mp3
```

### Tips
- You can leave links from earlier sessions in the box and just add new ones — already-downloaded tracks are automatically skipped.
- If a track is already in the format you picked (e.g. you choose FLAC and the source file is already FLAC), it's kept as-is rather than re-encoded, so you never lose quality unnecessarily.
- Re-running the app with a different format on the same links will download fresh copies in the new format (it won't overwrite/reuse the old ones, since the filename extension differs).

---

## 3. Using the command line (alternative)

1. Unzip the folder and open a terminal inside it.
2. Open `links.txt` and paste your links in (one per line — comments starting with `#` are ignored).
3. Run:
   ```
   python3 untitled_downloader.py
   ```
   To choose a format other than the default MP3:
   ```
   python3 untitled_downloader.py --format flac
   python3 untitled_downloader.py --format alac
   python3 untitled_downloader.py --format wav
   ```
   Supported values: `mp3`, `alac`, `wav`, `flac`, `aac`, `ogg`, `opus`.
4. Watch the terminal output. Files land in `Downloads/` when it prints `ALL DONE!`.

---

## 4. How it works, under the hood

- The script/app reads whatever links you provide and keeps only the ones matching:
  - `https://untitled.stream/library/project/...`
  - `https://samply.app/p/...`
- For **untitled.stream** links, it reads the page's embedded project data directly and downloads each track's signed audio URL in parallel.
- For **Samply** links, it uses Playwright to load the page in a headless browser (Samply doesn't expose a simple API), then either grabs the site's own "Download all as ZIP" or falls back to downloading each track's file individually.
- Every downloaded file is converted (or kept as-is, if it already matches your chosen format) using `ffmpeg`, and saved into a folder named after the project and creator.

---

## 5. Troubleshooting

- **"ffmpeg not found"** — install ffmpeg (see Requirements) and make sure it's on your system PATH, then restart the app.
- **Samply links do nothing / time out** — click **Install Samply support (Playwright)** in the app (or run the manual `pip install playwright && playwright install chromium` commands), then try again.
- **A track fails with an error in the log** — this usually means the link expired or the project's privacy settings block downloads. Re-check the link is still valid and shared/public.
- **App window doesn't open on Windows** — make sure Python was installed with "Add Python to PATH" checked; reinstall Python if unsure.

---

## 6. Other included scripts

- `convert_covers.py` — converts images in a local `Cover art` folder into PNGs.
- `merge_ye_albums.py` — a helper for de-duplicating lower-quality duplicate tracks in a library. Best handed to an AI coding assistant (e.g. Claude Code) to run interactively, since it needs judgment calls about which duplicates to keep.

---

Credits to enmilyisoffline, gliddd4, & icefields for their original work.