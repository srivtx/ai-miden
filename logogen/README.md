# LogoGen

A small logo generator using diffusion (DDPM).

## Workflow

### 1. You curate logos (on your laptop)

- Browse Pinterest / Behance / LogoPond
- Right-click → Save As on logos you like
- Collect 200-500 logos in a folder
- Zip the folder → upload to Colab

### 2. Train (on Colab T4, 30-60 min)

```
!unzip logos.zip -d /content/logos
!python logogen.py train --image-dir /content/logos --out-dir /content/logogen
```

Watch the loss drop. Samples are saved each epoch to `/content/logogen/samples_epoch_N.png`.

### 3. Generate

```
!python logogen.py sample --model /content/logogen/final.pt --out-dir /content/output --n 8
```

Generates 40 logos (8 per batch × 5 batches) in `/content/output/`.

## Tips

- Minimum 100 logos. 300+ is better.
- Square logos work better (CenterCrop handles rectangles).
- PNG with transparency → converted to RGB with white background by PIL.
- For 256×256 logos: `--image-size 256 --batch-size 4`.
- For faster training: `--image-size 64 --batch-size 32`.
- Adjust `--epochs` (default 50) and `--max-steps` (default 50000) for your dataset size.

## Memory

- 128×128, batch 16 → ~8GB VRAM (fits T4)
- 256×256, batch 4 → ~10GB VRAM (fits T4)
