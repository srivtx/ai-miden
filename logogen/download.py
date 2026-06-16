"""
Logo Downloader: fetch logo images from the web (no auth, no API key).

Uses DuckDuckGo image search to find logos matching the query.
Filters out tiny/broken results. Stops when n valid images are collected.

    !python download.py --out-dir /content/logos --n 300
"""

import os
import sys
import io
import time
import argparse
from pathlib import Path
from PIL import Image
import requests


def download_logos(out_dir, n=300, image_size=256, queries=None, retries=3):
    """Download ~n logo images from DuckDuckGo image search."""
    os.makedirs(out_dir, exist_ok=True)

    if queries is None:
        queries = [
            "minimal logo design",
            "clean modern company logo",
            "small app icon flat design",
            "monogram brand mark",
            "simple geometric logo",
            "creative letter mark logo",
            "modern abstract logo mark",
        ]

    per_query = max(30, n // len(queries))
    print(f"Will search {len(queries)} queries, up to {per_query} logos each")
    print(f"Target: {n} logos at {image_size}×{image_size}\n")

    # Install ddgs if needed
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        import subprocess
        print("Installing duckduckgo_search...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "duckduckgo_search", "-q"])
        from duckduckgo_search import DDGS

    total = 0
    for query in queries:
        if total >= n:
            break
        count = 0
        print(f"Searching: {query}")

        for attempt in range(retries):
            try:
                with DDGS() as ddgs:
                    results = ddgs.images(query, max_results=max(per_query * 3, 50))
                break
            except Exception as e:
                if attempt == retries - 1:
                    print(f"  Failed after {retries} attempts: {e}")
                    results = []
                else:
                    print(f"  Retry {attempt+1}: {e}")
                    time.sleep(2)

        for result in results:
            if total >= n:
                break
            url = result.get("image") or ""
            if not url or not (url.startswith("http://") or url.startswith("https://")):
                continue

            # Skip known bad hosts
            skip_hosts = ["facebook.com", "twitter.com", "instagram.com", "youtube.com",
                          "pinterest.com/js/", "google.com/ads", "doubleclick"]
            if any(h in url for h in skip_hosts):
                continue

            try:
                r = requests.get(url, timeout=8,
                                 headers={"User-Agent": "LogoDownloader/1.0"})
                if r.status_code != 200:
                    continue

                content_type = r.headers.get("content-type", "")
                if "svg" in content_type:
                    continue  # skip SVGs (need raster for PIL)

                img = Image.open(io.BytesIO(r.content)).convert("RGBA")

                # Skip tiny images
                if img.width < 80 or img.height < 80:
                    continue

                # Pad to square, then resize
                img = pad_to_square(img)
                img = img.resize((image_size, image_size), Image.LANCZOS)

                # Save
                name = f"{query.replace(' ', '_')}_{count:03d}.png"
                path = os.path.join(out_dir, name)
                img.save(path)

                count += 1
                total += 1
                if count % 10 == 0:
                    print(f"  {total} logos saved...", end="\r")

            except (requests.RequestException, OSError, Image.UnidentifiedImageError):
                continue

            # Gentle rate limit
            if count > 0 and count % 5 == 0:
                time.sleep(0.5)

        print(f"  {query}: {count} logos  (total: {total})")

    print(f"\nDone: {total} logos in {out_dir}/")
    return total


def pad_to_square(img):
    """Pad image to square with white background, keeping aspect ratio."""
    w, h = img.size
    if w == h:
        return img
    size = max(w, h)
    result = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    result.paste(img, ((size - w) // 2, (size - h) // 2), img if img.mode == "RGBA" else None)
    return result


def main():
    parser = argparse.ArgumentParser(description="Download logo images for Logogen")
    parser.add_argument("--out-dir", type=str, default="/content/logos")
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--image-size", type=int, default=256)
    args = parser.parse_args()

    download_logos(args.out_dir, n=args.n, image_size=args.image_size)


if __name__ == "__main__":
    main()
