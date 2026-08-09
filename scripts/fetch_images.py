#!/usr/bin/env python3
"""Fetch pool-themed stock photos from Pexels for Piscine Nette Salon."""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API_KEY = os.environ.get("PEXELS_API_KEY")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "image-manifest.json")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")
CREDITS_PATH = os.path.join(ASSETS_DIR, "CREDITS.md")

# Pexels sits behind Cloudflare, which blocks urllib's default
# "Python-urllib/x.y" User-Agent with a 403 — a browser-like UA is required
# for both the search API call and the image download itself.
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def search_photo(query):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": 5, "orientation": "landscape"}
    )
    req = urllib.request.Request(url, headers={"Authorization": API_KEY, "User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    photos = data.get("photos", [])
    if not photos:
        raise RuntimeError(f"No Pexels results for query: {query}")
    return photos[0]


def download(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def main():
    if not API_KEY:
        print("ERROR: set PEXELS_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    os.makedirs(ASSETS_DIR, exist_ok=True)
    credits_lines = ["# Image credits\n\n", "All photos from [Pexels](https://www.pexels.com), free to use.\n\n"]
    if os.path.exists(CREDITS_PATH):
        with open(CREDITS_PATH, encoding="utf-8") as f:
            existing = f.read()
    else:
        existing = ""

    for entry in manifest:
        dest = os.path.join(ASSETS_DIR, entry["filename"])
        if os.path.exists(dest):
            print(f"SKIP (already downloaded): {entry['filename']}")
            continue
        print(f"Searching: {entry['query']}")
        photo = search_photo(entry["query"])
        download(photo["src"]["large"], dest)
        credit_line = (
            f"- `{entry['filename']}` — photo by {photo['photographer']} "
            f"({photo['photographer_url']}) via Pexels: {photo['url']}\n"
        )
        credits_lines.append(credit_line)
        # Write credits immediately after each successful download (not only
        # at the end) so a partial run never loses attribution for the
        # images it did fetch.
        with open(CREDITS_PATH, "w", encoding="utf-8") as f:
            f.writelines(credits_lines)
        print(f"Saved: {dest}")
        time.sleep(1)


if __name__ == "__main__":
    main()
