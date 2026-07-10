import argparse
import urllib.parse
import urllib.request
import re
import json
import os
import subprocess
import zipfile
import concurrent.futures

# Configuration
LINKS_FILE = "links.txt"
OUTPUT_DIR = "Downloads"
API = "https://untitled.stream/api/storage/buckets/private-transcoded-audio/objects/{MUSIC_URL}/signedUrl?durationInSeconds=10800&cacheBufferInSeconds=600"
SAMPLY_CDN_URL = "https://cdn.samply.app/users/{USER_ID}/files/{FILE_ID}/output/aac256k@output.mp4"
SAMPLY_FILE_ID_RE = re.compile(r"/users/[^/]+/files/([^/]+)/output/")
MAX_MP3_CONVERT_SIZE_BYTES = 10 * 1024 * 1024

# Selectable output formats. "ext" is the output file extension, "ffmpeg_args"
# are the encoder args passed to ffmpeg (after "-vn"). ALAC is stored in an
# .m4a container, which is the standard Apple/iTunes-compatible way to ship it.
FORMAT_CONFIGS = {
    "mp3":  {"ext": ".mp3",  "ffmpeg_args": ["-c:a", "libmp3lame", "-q:a", "2"]},
    "alac": {"ext": ".m4a",  "ffmpeg_args": ["-c:a", "alac"]},
    "wav":  {"ext": ".wav",  "ffmpeg_args": ["-c:a", "pcm_s16le"]},
    "flac": {"ext": ".flac", "ffmpeg_args": ["-c:a", "flac"]},
    "aac":  {"ext": ".aac",  "ffmpeg_args": ["-c:a", "aac", "-b:a", "256k"]},
    "ogg":  {"ext": ".ogg",  "ffmpeg_args": ["-c:a", "libvorbis", "-q:a", "6"]},
    "opus": {"ext": ".opus", "ffmpeg_args": ["-c:a", "libopus", "-b:a", "160k"]},
}

# Set at runtime from --format (see main()). Kept as a module-level default so
# any function that doesn't explicitly receive a target_format still works.
TARGET_FORMAT = "mp3"

def get_extension_from_url(url):
    path = urllib.parse.urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lower()

def sanitize_stem(name):
    return sanitize(os.path.splitext(name)[0])

def should_keep_original(file_path, source_ext="", content_type="", target_format="mp3"):
    size = os.path.getsize(file_path)
    ext = (source_ext or os.path.splitext(file_path)[1]).lower()
    content_type = (content_type or "").lower()
    target_ext = FORMAT_CONFIGS[target_format]["ext"]

    # If the source is already in the requested format, don't re-encode it.
    if ext == target_ext:
        return True, f"Already {target_format.upper()}"

    # The old size/FLAC-based heuristics only make sense when the *target* is
    # the lossy MP3 format (they exist to avoid throwing away a
    # lossless/high-quality source for a lossy re-encode). For lossless or
    # otherwise-selected targets, we always convert to the chosen format.
    if target_format == "mp3":
        if ext == ".flac" or "flac" in content_type:
            return True, "FLAC source"
        if size > MAX_MP3_CONVERT_SIZE_BYTES:
            return True, f"File is over 10MB ({round(size / (1024 * 1024), 2)} MB)"

    return False, ""

def convert_or_keep_audio(temp_path, output_base_path, source_ext="", content_type="", target_format=None):
    target_format = target_format or TARGET_FORMAT
    config = FORMAT_CONFIGS[target_format]
    keep_original, reason = should_keep_original(
        temp_path, source_ext=source_ext, content_type=content_type, target_format=target_format
    )

    if keep_original:
        ext = source_ext.lower() if source_ext else os.path.splitext(temp_path)[1].lower()
        if not ext:
            ext = ".m4a"
        output_path = f"{output_base_path}{ext}"
        os.replace(temp_path, output_path)
        return output_path, f"Kept original ({reason})"

    output_path = f"{output_base_path}{config['ext']}"
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", temp_path,
        "-vn", *config["ffmpeg_args"],
        output_path
    ]
    subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
    os.remove(temp_path)
    return output_path, f"Converted to {target_format.upper()}"

def sanitize(name):
    # Remove characters that are unsafe for directory or file names
    return re.sub(r'[<>:"/\\|?*]', '_', str(name))

def scrape_untitled_track(track, dir_path, track_title):
    try:
        file_dir = urllib.parse.quote_plus(track['audio_fallback_url'].split('/', 7)[-1])
        signed_url_api = API.format(MUSIC_URL=file_dir)
        
        # Get the actual media URL from the signing API
        req = urllib.request.Request(signed_url_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            signed_info = json.loads(r.read().decode('utf-8'))
            source_url = signed_info['url']
            
            sanitized_track = sanitize_stem(track_title)
            target_ext = FORMAT_CONFIGS[TARGET_FORMAT]["ext"]
            existing_path = os.path.join(dir_path, f"{sanitized_track}{target_ext}")
            if os.path.exists(existing_path):
                return f"Skipped existing: {existing_path}"
            
            # Download file using memory efficient streaming
            source_ext = get_extension_from_url(source_url)
            if not source_ext:
                source_ext = ".m4a"
            temp_path = os.path.join(dir_path, f"_tmp_{sanitized_track}{source_ext}")

            req3 = urllib.request.Request(source_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req3, timeout=60) as response3:
                content_type = response3.headers.get("Content-Type", "")
                with open(temp_path, 'wb') as f:
                    while True:
                        chunk = response3.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            output_base_path = os.path.join(dir_path, sanitized_track)
            output_path, action = convert_or_keep_audio(
                temp_path,
                output_base_path,
                source_ext=source_ext,
                content_type=content_type
            )
            return f"Downloaded: {output_path} ({action})"
    except Exception as e:
        return f"Failed track: {track_title} - {e}"

def download_untitled_project(url):
    print(f"Fetching metadata for: {url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'window\.__remixContext = (.*?);</script>', html, re.DOTALL)
            if not match:
                print(f"No context data found on the page for {url}")
                return
            
            data = json.loads(match.group(1))
            loaderData = data['state']['loaderData']['routes/library.project.$projectSlug']
            
            project_info = loaderData['project']['project']
            title = project_info.get('title', 'Unknown Project')
            
            tracks = loaderData['project'].get('tracks', [])
            
            # Find creator username using the first track's username property
            creator = "Unknown Creator"
            if tracks and 'username' in tracks[0]:
                creator = tracks[0]['username']
            
            # Create "{Project_Title}, {Project_Creator}" directory structure
            folder_name = f"{sanitize(title)}, {sanitize(creator)}"
            dir_path = os.path.join(OUTPUT_DIR, folder_name)
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")
            
            # Download tracks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for track in tracks:
                    track_title = track.get('title', 'Unknown Track')
                    futures.append(executor.submit(scrape_untitled_track, track, dir_path, track_title))
                
                for future in concurrent.futures.as_completed(futures):
                    print(future.result())
                    
    except Exception as e:
        print(f"Error fetching/processing {url}: {e}")

def extract_samply_user_id(url):
    query = urllib.parse.urlparse(url).query
    params = urllib.parse.parse_qs(query)
    user_ids = params.get("si", [])
    return user_ids[0] if user_ids else None

def fetch_samply_metadata(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is required for Samply links. Install with: pip install playwright && playwright install chromium")
        return None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        observed_file_ids = []

        def on_request(request):
            req_url = request.url
            if "cdn.samply.app/users/" in req_url and "/files/" in req_url and "/output/" in req_url:
                match = SAMPLY_FILE_ID_RE.search(req_url)
                if match:
                    file_id = match.group(1)
                    if file_id not in observed_file_ids:
                        observed_file_ids.append(file_id)

        page.on("request", on_request)

        try:
            page.goto(url, wait_until="load", timeout=60000)
            page.wait_for_selector("[data-player-list-item-id]", timeout=30000)
            # Give Vue/Pinia time to hydrate track objects.
            try:
                page.wait_for_function(
                    "() => { const el = document.querySelector('[data-player-list-item-id]'); return !!(el && el.__vueParentComponent && (el.__vueParentComponent.ctx || el.__vueParentComponent.setupState)); }",
                    timeout=15000
                )
            except Exception:
                # Fallback path below handles non-exposed Vue internals.
                pass
        except Exception as e:
            browser.close()
            print(f"Error loading Samply page: {e}")
            return None

        metadata = page.evaluate("""
        () => {
            const titleFromPage = document.title.includes(' | Samply')
                ? document.title.split(' | Samply')[0].trim()
                : document.title.trim();
            const items = document.querySelectorAll('[data-player-list-item-id]');
            const tracks = [];
            const fallbackTrackNames = [];

            const artistFromMeta =
                document.querySelector('meta[property="og:site_name"]')?.getAttribute('content') ||
                document.querySelector('meta[name="author"]')?.getAttribute('content') ||
                document.querySelector('meta[property="og:title"]')?.getAttribute('content') ||
                null;

            for (const item of items) {
                const lines = (item.innerText || '').split('\\n').map(s => s.trim()).filter(Boolean);
                if (lines.length >= 2) {
                    fallbackTrackNames.push(lines[1]);
                }

                const comp = item.__vueParentComponent;
                const track = comp?.ctx?.track || comp?.setupState?.track || null;
                if (!track) continue;

                const fileId =
                    track.activeFileId ||
                    (Array.isArray(track.versions) && track.versions[0] ? track.versions[0].fileId : null) ||
                    null;
                if (!fileId) continue;

                tracks.push({
                    name: track.name || 'Unknown Track',
                    file_id: fileId,
                    creator:
                        comp?.ctx?.projectStore?.project?.artistName ||
                        comp?.setupState?.projectStore?.project?.artistName ||
                        'Unknown Creator'
                });
            }

            return {
                title: titleFromPage || 'Unknown Project',
                creator: artistFromMeta,
                tracks,
                fallback_track_names: fallbackTrackNames
            };
        }
        """)
        browser.close()

        if metadata.get("tracks"):
            return metadata

        # Fallback when Vue internals are not exposed:
        # map rendered track names to observed CDN file IDs in order.
        fallback_names = metadata.get("fallback_track_names", [])
        fallback_tracks = []
        for idx, file_id in enumerate(observed_file_ids):
            if idx >= len(fallback_names):
                break
            fallback_tracks.append({
                "name": fallback_names[idx],
                "file_id": file_id,
                "creator": metadata.get("creator") or "Unknown Creator"
            })

        return {
            "title": metadata.get("title", "Unknown Project"),
            "tracks": fallback_tracks
        }

def download_samply_track(track, user_id, dir_path):
    track_title = track.get("name", "Unknown Track")
    sanitized_track = sanitize_stem(track_title)
    target_ext = FORMAT_CONFIGS[TARGET_FORMAT]["ext"]
    existing_path = os.path.join(dir_path, f"{sanitized_track}{target_ext}")
    if os.path.exists(existing_path):
        return f"Skipped existing: {existing_path}"

    file_id = track.get("file_id")
    if not file_id:
        return f"Failed track: {track_title} - Missing file ID"

    temp_path = os.path.join(dir_path, f"temp_{file_id}.mp4")
    cdn_url = SAMPLY_CDN_URL.format(USER_ID=user_id, FILE_ID=file_id)

    try:
        req = urllib.request.Request(cdn_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            content_type = response.headers.get("Content-Type", "")
            with open(temp_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

        output_base_path = os.path.join(dir_path, sanitized_track)
        output_path, action = convert_or_keep_audio(
            temp_path,
            output_base_path,
            source_ext=".mp4",
            content_type=content_type
        )
        return f"Downloaded: {output_path} ({action})"
    except Exception as e:
        return f"Failed track: {track_title} - {e}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def download_samply_zip(url, dir_path):
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        return False, "Playwright is required for Samply ZIP download."

    os.makedirs(dir_path, exist_ok=True)
    zip_temp_path = os.path.join(dir_path, "_samply_download_all.zip")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            page.goto(url, wait_until="load", timeout=60000)

            # Try accessible-name first, then icon-only button detection.
            button = page.get_by_role("button", name=re.compile(r"download all as zip", re.I))
            if button.count() == 0:
                # Icon-only fallback: Samply download glyph has a baseline and downward arrow.
                icon_buttons = page.locator("button.base-button:has(svg)")
                found_icon_button = None
                for idx in range(icon_buttons.count()):
                    candidate = icon_buttons.nth(idx)
                    html = candidate.inner_html()
                    if "M15.5 15" in html and "13.2803" in html:
                        found_icon_button = candidate
                        break
                button = found_icon_button

            if not button:
                context.close()
                browser.close()
                return False, "Samply ZIP button not available on this page."

            with page.expect_download(timeout=180000) as download_info:
                button.click()
            download = download_info.value
            download.save_as(zip_temp_path)

            with zipfile.ZipFile(zip_temp_path, 'r') as zip_ref:
                zip_ref.extractall(dir_path)

            target_ext = FORMAT_CONFIGS[TARGET_FORMAT]["ext"]
            processed = 0
            for root, _, files in os.walk(dir_path):
                for file_name in files:
                    if file_name.startswith("_samply_download_all"):
                        continue
                    src_path = os.path.join(root, file_name)
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext not in {".mp3", ".m4a", ".mp4", ".aac", ".wav", ".flac", ".ogg", ".opus"}:
                        continue
                    if ext == target_ext:
                        continue

                    output_base = os.path.join(root, sanitize_stem(file_name))
                    converted_path, _ = convert_or_keep_audio(src_path, output_base, source_ext=ext)
                    processed += 1
                    if converted_path != src_path and os.path.exists(src_path):
                        os.remove(src_path)

            return True, f"Downloaded ZIP and extracted to: {dir_path} (processed {processed} audio file(s))"
        except PlaywrightTimeout:
            return False, "Timed out waiting for Samply ZIP download."
        except Exception as e:
            return False, f"Samply ZIP download failed: {e}"
        finally:
            if os.path.exists(zip_temp_path):
                os.remove(zip_temp_path)
            context.close()
            browser.close()

def download_samply_project(url):
    print(f"Fetching metadata for: {url}")
    user_id = extract_samply_user_id(url)
    if not user_id:
        print(f"Error: Missing 'si' parameter in Samply URL: {url}")
        return

    metadata = fetch_samply_metadata(url)
    if not metadata:
        return

    tracks = metadata.get("tracks", [])
    if not tracks:
        print(f"No downloadable tracks found on Samply page: {url}")
        print("This can happen if project data is still loading, or if downloads/access are restricted for this share.")
        return

    title = metadata.get("title", "Unknown Project")
    creator = tracks[0].get("creator", "Unknown Creator")
    folder_name = f"{sanitize(title)}, {sanitize(creator)}"
    dir_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(dir_path, exist_ok=True)
    print(f"Created directory: {dir_path}")

    zip_ok, zip_message = download_samply_zip(url, dir_path)
    if zip_ok:
        print(zip_message)
        return
    print(f"ZIP download unavailable, falling back to per-track mode. ({zip_message})")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(download_samply_track, track, user_id, dir_path) for track in tracks]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

def main():
    global TARGET_FORMAT

    parser = argparse.ArgumentParser(description="Batch download untitled.stream and Samply projects.")
    parser.add_argument(
        "-f", "--format",
        choices=sorted(FORMAT_CONFIGS.keys()),
        default="mp3",
        help="Output audio format for downloaded tracks (default: mp3)."
    )
    args = parser.parse_args()
    TARGET_FORMAT = args.format
    print(f"Output format: {TARGET_FORMAT.upper()} (.{FORMAT_CONFIGS[TARGET_FORMAT]['ext'].lstrip('.')})")

    if not os.path.exists(LINKS_FILE):
        print(f"'{LINKS_FILE}' not found. Please create it and put the project URLs inside, one per line.")
        return
        
    with open(LINKS_FILE, 'r') as f:
        urls = []
        for line in f:
            urls.extend(re.findall(r"https?://[^\s]+", line))

    valid_urls = [
        url for url in urls
        if "untitled.stream/library/project/" in url or "samply.app/p/" in url
    ]
        
    if not valid_urls:
        print(f"No valid untitled.stream or samply.app links found in '{LINKS_FILE}'.")
        return
        
    print(f"Loaded {len(valid_urls)} project(s) to download.")
    for idx, url in enumerate(valid_urls):
        print(f"\n--- Processing [{idx+1}/{len(valid_urls)}] ---")
        if "untitled.stream/library/project/" in url:
            download_untitled_project(url)
        else:
            download_samply_project(url)
        
    print("\n🎉 ALL DONE!")

if __name__ == "__main__":
    main()
