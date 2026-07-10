#!/usr/bin/env python3
"""
Untitled.stream + Samply Downloader — GUI

A simple point-and-click front end for untitled_downloader.py. No terminal
flags or text-file editing required: paste links, pick a format, click
Download.
"""

import os
import re
import sys
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

import untitled_downloader as ud

APP_TITLE = "Untitled.stream / Samply Downloader"
LINKS_PATTERN = re.compile(r"https?://[^\s]+")


class QueueWriter:
    """A file-like object that pushes writes into a queue instead of a real stream,
    so background-thread print() calls can be safely shown in the Tk UI thread."""
    def __init__(self, q):
        self.q = q

    def write(self, text):
        if text:
            self.q.put(text)

    def flush(self):
        pass


class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("760x640")
        self.root.minsize(600, 500)

        self.log_queue = queue.Queue()
        self.worker_thread = None

        self._build_layout()
        self._load_existing_links()
        self.root.after(100, self._poll_log)

    # ---------------------------------------------------------------- UI ---
    def _build_layout(self):
        pad = {"padx": 12, "pady": 8}

        header = ttk.Frame(self.root)
        header.pack(fill="x", **pad)
        ttk.Label(
            header, text=APP_TITLE, font=("Helvetica", 15, "bold")
        ).pack(side="left")

        # Links box
        links_frame = ttk.LabelFrame(self.root, text="Paste untitled.stream / samply.app links (one per line)")
        links_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.links_box = scrolledtext.ScrolledText(links_frame, height=10, wrap="word")
        self.links_box.pack(fill="both", expand=True, padx=8, pady=8)

        # Options row
        options = ttk.Frame(self.root)
        options.pack(fill="x", padx=12, pady=(0, 8))

        ttk.Label(options, text="Output format:").pack(side="left")
        self.format_var = tk.StringVar(value="mp3")
        format_names = sorted(ud.FORMAT_CONFIGS.keys())
        self.format_menu = ttk.Combobox(
            options, textvariable=self.format_var, values=format_names,
            state="readonly", width=8
        )
        self.format_menu.pack(side="left", padx=(6, 20))

        self.download_btn = ttk.Button(options, text="Download", command=self.start_download)
        self.download_btn.pack(side="left")

        self.open_folder_btn = ttk.Button(
            options, text="Open Downloads Folder", command=self.open_downloads_folder
        )
        self.open_folder_btn.pack(side="left", padx=8)

        self.setup_btn = ttk.Button(
            options, text="Install Samply support (Playwright)", command=self.install_playwright
        )
        self.setup_btn.pack(side="right")

        # Status / requirements line
        self.status_var = tk.StringVar(value=self._requirements_status())
        ttk.Label(self.root, textvariable=self.status_var, foreground="#555").pack(
            fill="x", padx=12
        )

        # Log box
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log_box = scrolledtext.ScrolledText(log_frame, height=14, state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)

    def _requirements_status(self):
        ffmpeg_ok = shutil.which("ffmpeg") is not None
        try:
            import playwright  # noqa: F401
            playwright_ok = True
        except ImportError:
            playwright_ok = False
        parts = [
            f"ffmpeg: {'found' if ffmpeg_ok else 'NOT FOUND (required — install it and restart this app)'}",
            f"Playwright (needed for Samply links): {'installed' if playwright_ok else 'not installed — use the button on the right'}",
        ]
        return "  |  ".join(parts)

    def _load_existing_links(self):
        if os.path.exists(ud.LINKS_FILE):
            try:
                with open(ud.LINKS_FILE, "r") as f:
                    contents = f.read()
                # Only pre-fill with actual links, skip the instructional comments.
                urls = LINKS_PATTERN.findall(contents)
                if urls:
                    self.links_box.insert("1.0", "\n".join(urls))
            except Exception:
                pass

    # ----------------------------------------------------------- actions ---
    def start_download(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return

        raw_text = self.links_box.get("1.0", tk.END)
        urls = LINKS_PATTERN.findall(raw_text)
        valid_urls = [
            u for u in urls
            if "untitled.stream/library/project/" in u or "samply.app/p/" in u
        ]

        if not valid_urls:
            messagebox.showwarning(
                APP_TITLE,
                "No valid untitled.stream or samply.app links found.\n\n"
                "Paste links like:\n"
                "https://untitled.stream/library/project/...\n"
                "https://samply.app/p/..."
            )
            return

        if shutil.which("ffmpeg") is None:
            if not messagebox.askyesno(
                APP_TITLE,
                "ffmpeg was not found on your system. Downloads will fail for any "
                "track that needs conversion.\n\nContinue anyway?"
            ):
                return

        self.download_btn.config(state="disabled")
        self._log_clear()
        self.worker_thread = threading.Thread(
            target=self._run_worker, args=(valid_urls, self.format_var.get()), daemon=True
        )
        self.worker_thread.start()

    def _run_worker(self, urls, fmt):
        ud.TARGET_FORMAT = fmt
        old_stdout = sys.stdout
        sys.stdout = QueueWriter(self.log_queue)
        try:
            print(f"Output format: {fmt.upper()}")
            print(f"Loaded {len(urls)} project(s) to download.")
            for idx, url in enumerate(urls):
                print(f"\n--- Processing [{idx + 1}/{len(urls)}] ---")
                if "untitled.stream/library/project/" in url:
                    ud.download_untitled_project(url)
                else:
                    ud.download_samply_project(url)
            print("\nALL DONE!")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
        finally:
            sys.stdout = old_stdout
            self.log_queue.put("__DONE__")

    def install_playwright(self):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo(APP_TITLE, "Please wait for the current download to finish first.")
            return

        self.setup_btn.config(state="disabled")
        self._log_clear()
        threading.Thread(target=self._run_install_playwright, daemon=True).start()

    def _run_install_playwright(self):
        old_stdout = sys.stdout
        sys.stdout = QueueWriter(self.log_queue)
        try:
            print("Installing Playwright (this may take a minute)...\n")
            steps = [
                [sys.executable, "-m", "pip", "install", "playwright"],
                [sys.executable, "-m", "playwright", "install", "chromium"],
            ]
            for cmd in steps:
                print(f"$ {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                print(result.stdout)
                if result.returncode != 0:
                    print(result.stderr)
                    print("\nInstall failed. You can also run these commands manually in a terminal.")
                    return
            print("\nPlaywright installed. Samply links are now supported.")
        finally:
            sys.stdout = old_stdout
            self.log_queue.put("__INSTALL_DONE__")

    def open_downloads_folder(self):
        folder = os.path.abspath(ud.OUTPUT_DIR)
        os.makedirs(folder, exist_ok=True)
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", folder])
            elif sys.platform.startswith("win"):
                os.startfile(folder)  # noqa
            else:
                subprocess.run(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Couldn't open the folder automatically.\nIt's located at:\n{folder}\n\n({e})")

    # ------------------------------------------------------------- log ---
    def _log_clear(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state="disabled")

    def _log_write(self, text):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, text)
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def _poll_log(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if msg == "__DONE__":
                    self.download_btn.config(state="normal")
                    self.status_var.set(self._requirements_status())
                    messagebox.showinfo(APP_TITLE, "Downloads complete! Click 'Open Downloads Folder' to view your files.")
                elif msg == "__INSTALL_DONE__":
                    self.setup_btn.config(state="normal")
                    self.status_var.set(self._requirements_status())
                else:
                    self._log_write(msg)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log)


def main():
    root = tk.Tk()
    DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
