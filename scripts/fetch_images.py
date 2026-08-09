#!/usr/bin/env python3
"""Fetch pool-themed stock photos from Pexels for Piscine Nette Salon."""
import json
import os
import re
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


def search_photo(query, used_ids):
    """Return the first result for `query` whose Pexels photo id hasn't
    already been used elsewhere in this run.

    Different manifest queries can return the same top result (Pexels has a
    limited pool of pool photos), which previously produced byte-identical
    "duplicate" images across unrelated village pages. Tracking used ids lets
    us fall back to the next-best result in the same 5-photo search instead.
    """
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": 5, "orientation": "landscape"}
    )
    req = urllib.request.Request(url, headers={"Authorization": API_KEY, "User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    photos = data.get("photos", [])
    if not photos:
        raise RuntimeError(f"No Pexels results for query: {query}")
    for photo in photos:
        if photo["id"] not in used_ids:
            return photo
    raise RuntimeError(
        f"All {len(photos)} Pexels results for query {query!r} are already "
        "used by other manifest entries in this run"
    )


def download(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


CREDIT_LINE_RE = re.compile(r"^- `([^`]+)` — (.+)$")
PEXELS_PHOTO_ID_RE = re.compile(r"-(\d+)/?\s*$")


def extract_photo_id(credit_line):
    """Pull the trailing Pexels photo id out of a credit line's URL, e.g.
    ".../photo/woman-relaxing-in-pool-at-roccabruna-france-38572363/" -> 38572363.
    Returns None if the line doesn't match the expected shape.
    """
    match = PEXELS_PHOTO_ID_RE.search(credit_line.strip())
    return int(match.group(1)) if match else None


def load_existing_credits():
    """Parse assets/CREDITS.md (if present) into {filename: full_credit_line}.

    The stored line keeps its trailing newline so it can be reused verbatim
    when rewriting the file.
    """
    credits_by_file = {}
    if not os.path.exists(CREDITS_PATH):
        return credits_by_file
    with open(CREDITS_PATH, encoding="utf-8") as f:
        for line in f:
            match = CREDIT_LINE_RE.match(line.rstrip("\n"))
            if match:
                filename = match.group(1)
                credits_by_file[filename] = line if line.endswith("\n") else line + "\n"
    return credits_by_file


def write_credits(manifest, credits_by_file):
    lines = ["# Image credits\n\n", "All photos from [Pexels](https://www.pexels.com), free to use.\n\n"]
    for entry in manifest:
        filename = entry["filename"]
        if filename in credits_by_file:
            lines.append(credits_by_file[filename])
    with open(CREDITS_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main():
    if not API_KEY:
        print("ERROR: set PEXELS_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    os.makedirs(ASSETS_DIR, exist_ok=True)
    credits_by_file = load_existing_credits()
    # Seed used_ids from already-downloaded photos too (e.g. pelissanne.jpg,
    # which we keep as-is), so a re-run never picks a "new" photo that
    # duplicates one already committed for another village.
    used_ids = {
        photo_id
        for line in credits_by_file.values()
        if (photo_id := extract_photo_id(line)) is not None
    }

    for entry in manifest:
        dest = os.path.join(ASSETS_DIR, entry["filename"])
        if os.path.exists(dest):
            print(f"SKIP (already downloaded): {entry['filename']}")
        else:
            print(f"Searching: {entry['query']}")
            photo = search_photo(entry["query"], used_ids)
            used_ids.add(photo["id"])
            download(photo["src"]["large"], dest)
            credit_line = (
                f"- `{entry['filename']}` — photo by {photo['photographer']} "
                f"({photo['photographer_url']}) via Pexels: {photo['url']}\n"
            )
            credits_by_file[entry["filename"]] = credit_line
            print(f"Saved: {dest}")
            time.sleep(1)
        # Rewrite credits after each entry (whether skipped or downloaded) so
        # a partial run never loses attribution for pre-existing files and
        # CREDITS.md always reflects the full, correctly-ordered set.
        write_credits(manifest, credits_by_file)


if __name__ == "__main__":
    main()
