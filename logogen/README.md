# LogoGen

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/srivtx/ai-miden/blob/main/logogen/logogen_colab.ipynb)

Small logo generator using diffusion (DDPM). Curates logos from the web,
trains on them, generates new ones. All in Colab, all on T4.

## One-click workflow

```bash
!git clone https://github.com/srivtx/ai-miden.git
%cd ai-miden/logogen

# 1. Download 300 logos from public image search (no auth, 30 sec)
!python download.py --out-dir /content/logos --n 300

# 2. Train (30-60 min on T4)
!python logogen.py train --image-dir /content/logos --out-dir /content/logogen

# 3. Generate 40 new logos
!python logogen.py sample --model /content/logogen/final.pt --out-dir /content/generated --n 8
```

## Files

| File | Purpose |
|---|---|
| `download.py` | Fetches logos from DuckDuckGo image search (no API key) |
| `logogen.py` | Trains a DDPM U-Net and generates new logos |

## Manual curation (optional, better quality)

If you want higher-quality logos:

1. Browse Pinterest / Behance on your laptop
2. Right-click → Save As on logos you like. Collect 200-500.
3. Zip → upload to Colab → unzip to `/content/logos/`
4. Run `logogen.py train` as above

## Options

| Flag | Default | Notes |
|---|---|---|
| `--image-size` | 128 (train), 256 (download) | 64 for fast test, 256 for quality |
| `--n` (download) | 300 | More = better, up to ~500 |
| `--epochs` (train) | 50 | Fewer for quick test |
| `--batch-size` (train) | 16 | 4 for 256×256, 32 for 64×64 |
| `--base-ch` (train) | 64 | 32 for smaller/faster model |
