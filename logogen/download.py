"""
Logo Downloader: fetch logo images from the web.

Tries multiple sources in order:
  1. Pexels API (free, 200 requests/hour, needs key but we provide a demo key)
  2. Synthetic generation (always works, colored geometric shapes)

    !python download.py --out-dir /content/logos --n 300
"""

import os
import sys
import io
import time
import random
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import requests


def generate_synthetic_logo(size=256):
    """Generate a logo-like geometric image."""
    bg = random.choice(['#FFFFFF', '#F8F9FA', '#FAFBFC', '#F5F0EB'])
    img = Image.new('RGB', (size, size), bg)
    draw = ImageDraw.Draw(img)

    palette = ['#FF4757', '#2ED573', '#1E90FF', '#A55EEA', '#FFA502',
               '#FF6348', '#00D2D3', '#FECA57', '#5F27CD', '#01A3A4',
               '#E056A0', '#222F3E', '#10AC84', '#EE5A24', '#0ABDE3']

    styles = [
        'single_circle', 'single_rect', 'overlapping_shapes',
        'letter', 'line_art', 'diagonal', 'three_dots',
        'half_circle', 'border_frame', 'centered_triangle'
    ]
    style = random.choice(styles)
    color = random.choice(palette)
    color2 = random.choice(palette)

    if style == 'single_circle':
        r = random.randint(40, 90)
        x, y = random.randint(r + 5, size - r - 5), random.randint(r + 5, size - r - 5)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    elif style == 'single_rect':
        w, h = random.randint(50, 100), random.randint(40, 80)
        x, y = random.randint(10, size - w - 10), random.randint(10, size - h - 10)
        rnd = random.randint(0, 20)
        draw.rounded_rectangle([x, y, x + w, y + h], radius=rnd, fill=color)

    elif style == 'overlapping_shapes':
        r = random.randint(40, 70)
        x1 = size // 2 - random.randint(10, 30)
        y1 = size // 2
        draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=color)
        x2 = size // 2 + random.randint(10, 30)
        draw.ellipse([x2 - r, y2 := size // 2, x2 + r, y2 + r], fill=color2,
                     outline=None if random.random() > 0.5 else '#FFF')

    elif style == 'letter':
        letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        fs = random.randint(60, 120)
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)
        except (OSError, IOError):
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), letter, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = (size - tw) // 2, (size - th) // 2 - random.randint(0, 20)
        draw.text((x, y), letter, fill=color, font=font,
                  stroke_fill=color2 if random.random() > 0.7 else None,
                  stroke_width=random.randint(1, 4))

    elif style == 'line_art':
        for _ in range(random.randint(3, 8)):
            x1, y1 = random.randint(10, size - 10), random.randint(10, size - 10)
            x2, y2 = random.randint(10, size - 10), random.randint(10, size - 10)
            draw.line([x1, y1, x2, y2], fill=color, width=random.randint(3, 15))

    elif style == 'diagonal':
        pts = [(0, random.randint(0, 40)), (size, random.randint(size - 40, size))]
        draw.polygon(pts + [(size, size), (0, size)], fill=color)
        pts2 = [(0, random.randint(0, 20)), (size, random.randint(size - 20, size))]
        draw.polygon(pts2 + [(size, 0), (0, 0)], fill=color2)

    elif style == 'three_dots':
        for i in range(3):
            r = random.randint(15, 30)
            x = size // 4 + i * size // 4 + random.randint(-20, 20)
            y = size // 2 + random.randint(-30, 30)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=palette[i % len(palette)])

    elif style == 'half_circle':
        r = random.randint(50, 90)
        x, y = size // 2, size // 2
        draw.pieslice([x - r, y - r, x + r, y + r],
                      start=random.randint(0, 270),
                      end=random.randint(90, 360),
                      fill=color)
        draw.pieslice([x - r + 20, y - r + 20, x + r - 20, y + r - 20],
                      start=random.randint(0, 270),
                      end=random.randint(90, 360),
                      fill=color2)

    elif style == 'border_frame':
        margin = random.randint(10, 30)
        thickness = random.randint(4, 15)
        draw.rectangle([margin, margin, size - margin, size - margin],
                       outline=color, width=thickness)
        inner = random.randint(size // 3, size // 2)
        cx, cy = size // 2, size // 2
        r = inner // 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color2)

    elif style == 'centered_triangle':
        cx, cy = size // 2, size // 2
        s = random.randint(50, 90)
        h = int(s * 0.866)
        pts = [(cx, cy - h // 2), (cx - s // 2, cy + h // 2), (cx + s // 2, cy + h // 2)]
        draw.polygon(pts, fill=color)
        # Add small circle at center
        r = random.randint(8, 20)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill='#FFFFFF' if bg != '#FFFFFF' else color2)

    return img


def download_pexels(out_dir, n=200, image_size=256):
    """Download from Pexels API. Needs PEXELS_API_KEY env var or default demo key."""
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        print("  No PEXELS_API_KEY set. Using synthetic generation.")
        return 0

    os.makedirs(out_dir, exist_ok=True)
    queries = ['minimal logo', 'geometric design', 'brand mark', 'modern icon']
    headers = {'Authorization': api_key}
    total = 0

    for query in queries:
        if total >= n:
            break
        per_page = min(80, n - total)
        try:
            r = requests.get(
                f'https://api.pexels.com/v1/search?query={query}&per_page={per_page}&orientation=square',
                headers=headers, timeout=15)
            if r.status_code != 200:
                print(f"  Pexels returned {r.status_code}")
                continue
            data = r.json()
            for photo in data.get('photos', []):
                src = photo['src'].get('large') or photo['src'].get('medium')
                if not src:
                    continue
                try:
                    img_data = requests.get(src, timeout=10).content
                    img = Image.open(io.BytesIO(img_data)).convert('RGB')
                    img = pad_to_square(img)
                    img = img.resize((image_size, image_size), Image.LANCZOS)
                    img.save(os.path.join(out_dir, f'pexels_{total:04d}.png'))
                    total += 1
                except Exception:
                    continue
                if total >= n:
                    break
            print(f"  {query}: {total} logos")
        except Exception as e:
            print(f"  Pexels error: {e}")
    return total


def pad_to_square(img):
    w, h = img.size
    if w == h:
        return img
    size = max(w, h)
    result = Image.new("RGB", (size, size), (255, 255, 255))
    result.paste(img, ((size - w) // 2, (size - h) // 2))
    return result


def main():
    parser = argparse.ArgumentParser(description="Download logo images for Logogen")
    parser.add_argument("--out-dir", type=str, default="/content/logos")
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--image-size", type=int, default=256)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Try Pexels first
    print(f"Downloading {args.n} logos at {args.image_size}x{args.image_size}...")
    pexels_count = download_pexels(args.out_dir, n=args.n, image_size=args.image_size)

    # Fill remaining with synthetic
    remaining = args.n - pexels_count
    if remaining > 0:
        print(f"\nGenerating {remaining} synthetic logos as fallback...")
        for i in range(remaining):
            img = generate_synthetic_logo(args.image_size)
            img.save(os.path.join(args.out_dir, f'synth_{i:04d}.png'))
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{remaining}")
        print(f"  Generated {remaining} synthetic logos")

    print(f"\nDone: {args.n} logos in {args.out_dir}/")
    print("(Synthetic logos are colored geometric shapes.)")
    print("For better quality: set PEXELS_API_KEY or upload your own.")
    print("Get a free Pexels key at https://www.pexels.com/api/")


if __name__ == "__main__":
    main()
