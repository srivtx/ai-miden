"""
LogoGen: a small logo generator using diffusion (DDPM).

You browse Pinterest/Behance, save ~200-500 logos to a folder,
zip and upload to Colab. LogoGen trains a small U-Net on your
curated logos and generates new ones.

    !python logogen.py train --image-dir /content/logos --out /content/logogen.pt
    !python logogen.py sample --model /content/logogen.pt --n 10 --out-dir /content/output
"""

import os
import math
import argparse
import random
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image, ImageDraw

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
# Data
# =============================================================================

class LogoDataset(Dataset):
    """Loads .png/.jpg/.jpeg from a directory, resizes to target size."""

    def __init__(self, root_dir, image_size=128):
        self.image_size = image_size
        self.paths = []
        for ext in ('*.png', '*.jpg', '*.jpeg', '*.webp', '*.PNG', '*.JPG'):
            self.paths.extend(Path(root_dir).rglob(ext))
        if not self.paths:
            raise ValueError(f"No images found in {root_dir}")

        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.CenterCrop((image_size, image_size)),
            transforms.ToTensor(),  # [0, 1], shape (C, H, W)
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),  # [-1, 1]
        ])
        self.augment = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.CenterCrop((image_size, image_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        img = Image.open(self.paths[idx]).convert('RGB')
        if random.random() < 0.4:  # augment 40% of the time
            return self.augment(img)
        return self.transform(img)


# =============================================================================
# U-Net for DDPM
# =============================================================================

def sinusoidal_embedding(t, dim):
    """Create sinusoidal position embeddings for timesteps."""
    device = t.device
    half_dim = dim // 2
    emb = math.log(10000) / (half_dim - 1)
    emb = torch.exp(torch.arange(half_dim, device=device, dtype=torch.float32) * -emb)
    emb = t.float()[:, None] * emb[None, :]
    emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=1)
    return emb


class ResBlock(nn.Module):
    """Residual block with time conditioning."""
    def __init__(self, in_ch, out_ch, time_dim, dropout=0.1):
        super().__init__()
        self.norm1 = nn.GroupNorm(8, in_ch)
        self.conv1 = nn.Conv2d(in_ch, out_ch, 3, padding=1)
        self.norm2 = nn.GroupNorm(8, out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, 3, padding=1)
        self.time_proj = nn.Linear(time_dim, out_ch)
        self.skip = nn.Conv2d(in_ch, out_ch, 1) if in_ch != out_ch else nn.Identity()

    def forward(self, x, t_emb):
        h = self.conv1(F.silu(self.norm1(x)))
        h = h + self.time_proj(F.silu(t_emb))[:, :, None, None]
        h = self.conv2(F.silu(self.norm2(h)))
        return h + self.skip(x)


class AttnBlock(nn.Module):
    """Self-attention block."""
    def __init__(self, ch):
        super().__init__()
        self.norm = nn.GroupNorm(8, ch)
        self.qkv = nn.Conv2d(ch, ch * 3, 1)
        self.proj = nn.Conv2d(ch, ch, 1)

    def forward(self, x):
        B, C, H, W = x.shape
        h = self.norm(x)
        q, k, v = self.qkv(h).reshape(B, 3, C, H * W).unbind(1)
        attn = torch.einsum('bci,bcj->bij', q, k) * (C ** -0.5)
        attn = F.softmax(attn, dim=-1)
        h = torch.einsum('bij,bcj->bci', attn, v).reshape(B, C, H, W)
        return x + self.proj(h)


class DownBlock(nn.Module):
    def __init__(self, in_ch, out_ch, time_dim, has_attn=False):
        super().__init__()
        self.res1 = ResBlock(in_ch, out_ch, time_dim)
        self.res2 = ResBlock(out_ch, out_ch, time_dim)
        self.attn = AttnBlock(out_ch) if has_attn else nn.Identity()
        self.down = nn.Conv2d(out_ch, out_ch, 3, stride=2, padding=1)

    def forward(self, x, t_emb):
        h = self.res1(x, t_emb)
        h = self.res2(h, t_emb)
        h = self.attn(h)
        return self.down(h), h  # return downsampled + skip


class UpBlock(nn.Module):
    def __init__(self, in_ch, out_ch, time_dim, has_attn=False):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_ch, out_ch, 2, stride=2)
        self.res1 = ResBlock(out_ch * 2, out_ch, time_dim)  # cat with skip
        self.res2 = ResBlock(out_ch, out_ch, time_dim)
        self.attn = AttnBlock(out_ch) if has_attn else nn.Identity()

    def forward(self, x, skip, t_emb):
        h = self.up(x)
        h = torch.cat([h, skip], dim=1)
        h = self.res1(h, t_emb)
        h = self.res2(h, t_emb)
        h = self.attn(h)
        return h


class LogoUNet(nn.Module):
    """Small U-Net for 128x128 RGB logo generation."""
    def __init__(self, img_ch=3, base_ch=64, ch_mults=(1, 2, 4, 8),
                 n_res_blocks=2, time_dim=256, dropout=0.1):
        super().__init__()
        self.time_dim = time_dim
        self.base_ch = base_ch

        # Time embedding
        self.time_mlp = nn.Sequential(
            nn.Linear(time_dim, time_dim * 4),
            nn.SiLU(),
            nn.Linear(time_dim * 4, time_dim * 4),
            nn.SiLU(),
            nn.Linear(time_dim * 4, time_dim),
        )

        # Input
        self.conv_in = nn.Conv2d(img_ch, base_ch, 3, padding=1)

        # Encoder — each level outputs (downsampled_tensor, skip_connection)
        in_ch = base_ch
        self.enc_blocks = nn.ModuleList()
        self.enc_out_chs = []  # skip channel counts, for decoder
        for i, mult in enumerate(ch_mults):
            out_ch = base_ch * mult
            has_attn = (i >= len(ch_mults) - 2)
            self.enc_blocks.append(DownBlock(in_ch, out_ch, time_dim, has_attn=has_attn))
            self.enc_out_chs.append(out_ch)
            in_ch = out_ch

        # Bottleneck
        bot_ch = base_ch * ch_mults[-1]
        self.bot_res1 = ResBlock(bot_ch, bot_ch, time_dim)
        self.bot_attn = AttnBlock(bot_ch)
        self.bot_res2 = ResBlock(bot_ch, bot_ch, time_dim)

        # Decoder — symmetric to encoder
        self.dec_blocks = nn.ModuleList()
        rev_mults = list(reversed(ch_mults))
        for i, mult in enumerate(rev_mults):
            out_ch = base_ch * mult
            has_attn = (i < 2)
            self.dec_blocks.append(UpBlock(in_ch, out_ch, time_dim, has_attn=has_attn))
            in_ch = out_ch

        # Output
        self.norm_out = nn.GroupNorm(8, base_ch)
        self.conv_out = nn.Conv2d(base_ch, img_ch, 3, padding=1)

    def forward(self, x, t):
        t_emb = sinusoidal_embedding(t, self.time_dim)
        t_emb = self.time_mlp(t_emb)

        h = self.conv_in(x)
        skips = []
        for block in self.enc_blocks:
            h, skip = block(h, t_emb)
            skips.append(skip)

        h = self.bot_res1(h, t_emb)
        h = self.bot_attn(h)
        h = self.bot_res2(h, t_emb)

        for block in self.dec_blocks:
            h = block(h, skips.pop(), t_emb)

        h = self.conv_out(F.silu(self.norm_out(h)))
        return h


# =============================================================================
# DDPM noise schedule
# =============================================================================

def make_beta_schedule(T=1000, s=0.008):
    """Linear schedule, same as DDPM paper."""
    steps = T + 1
    t = torch.linspace(0, T, steps)
    beta = torch.linspace(s, 0.02, steps)
    alpha = 1 - beta
    alpha_bar = torch.cumprod(alpha, dim=0)
    return beta, alpha_bar


# =============================================================================
# Training
# =============================================================================

def train(args):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Data
    ds = LogoDataset(args.image_dir, image_size=args.image_size)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True, num_workers=2,
                    pin_memory=True)
    print(f"Images: {len(ds)}, batches: {len(dl)}")

    # Model
    model = LogoUNet(img_ch=3, base_ch=args.base_ch).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model: {n_params:,} params")

    # DDPM schedule
    beta, alpha_bar = make_beta_schedule(T=args.timesteps)
    beta = beta.to(device)
    alpha_bar = alpha_bar.to(device)

    # Optimizer
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
    scaler = torch.cuda.amp.GradScaler() if device == 'cuda' else None

    # Training
    model.train()
    step = 0
    total_loss = 0
    best_loss = float('inf')
    os.makedirs(args.out_dir, exist_ok=True)

    print(f"Training {args.epochs} epochs ({len(dl)} batches/epoch)...")
    for epoch in range(args.epochs):
        for x in dl:
            if step >= args.max_steps:
                break
            x = x.to(device)
            B = x.shape[0]

            # Sample random timesteps
            t = torch.randint(0, args.timesteps, (B,), device=device)

            # Forward diffusion: x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * noise
            noise = torch.randn_like(x)
            a_bar = alpha_bar[t].view(B, 1, 1, 1)
            x_t = torch.sqrt(a_bar) * x + torch.sqrt(1 - a_bar) * noise

            # Predict noise
            with torch.cuda.amp.autocast() if scaler else torch.no_grad():
                pred = model(x_t, t)
                loss = F.mse_loss(pred, noise)

            opt.zero_grad()
            if scaler:
                scaler.scale(loss).backward()
                scaler.unscale_(opt)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(opt)
                scaler.update()
            else:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()

            total_loss += loss.item()
            step += 1

            if step % 100 == 0:
                avg = total_loss / 100
                total_loss = 0
                print(f"Epoch {epoch} | step {step:5d} | loss {avg:.4f}")
                if avg < best_loss:
                    best_loss = avg
                    torch.save(model.state_dict(), os.path.join(args.out_dir, 'best.pt'))

            if step >= args.max_steps:
                break
        # Sample each epoch
        if (epoch + 1) % max(1, args.epochs // 5) == 0:
            sample_path = os.path.join(args.out_dir, f'samples_epoch_{epoch+1}.png')
            generate_samples(model, device, beta, alpha_bar, args, save_path=sample_path, n=4)
        if step >= args.max_steps:
            break

    # Save final
    torch.save(model.state_dict(), os.path.join(args.out_dir, 'final.pt'))
    print(f"\nBest loss: {best_loss:.4f}")
    print(f"Saved to {args.out_dir}/")


def generate_samples(model, device, beta, alpha_bar, args, save_path=None, n=8):
    """Generate n logo samples using DDPM reverse process."""
    model.eval()
    img_size = args.image_size
    T = args.timesteps

    with torch.no_grad():
        x = torch.randn(n, 3, img_size, img_size, device=device)

        for t in reversed(range(T)):
            t_batch = torch.full((n,), t, device=device, dtype=torch.long)
            pred_noise = model(x, t_batch)

            beta_t = beta[t]
            alpha_t = 1 - beta_t
            alpha_bar_t = alpha_bar[t]
            alpha_bar_prev = alpha_bar[t - 1] if t > 0 else torch.tensor(1.0, device=device)

            # DDPM posterior mean
            coef1 = (beta_t / torch.sqrt(1 - alpha_bar_t))
            mean = (x - coef1 * pred_noise) / torch.sqrt(alpha_t)

            if t > 0:
                # Posterior variance
                beta_tilde = beta_t * (1 - alpha_bar_prev) / (1 - alpha_bar_t)
                noise = torch.randn_like(x)
                x = mean + torch.sqrt(beta_tilde) * noise
            else:
                x = mean

        # Denormalize: [-1, 1] -> [0, 1]
        x = (x + 1) / 2
        x = torch.clamp(x, 0, 1)

    if save_path:
        grid = make_grid(x, ncols=min(4, n))
        grid_np = (grid.permute(1, 2, 0).cpu().numpy() * 255).astype('uint8')
        Image.fromarray(grid_np).save(save_path)
        print(f"  samples saved to {save_path}")

    model.train()
    return x


def make_grid(images, ncols=4):
    """Create a grid of images."""
    B, C, H, W = images.shape
    nrows = (B + ncols - 1) // ncols
    grid = torch.zeros(C, nrows * H, ncols * W)
    for i in range(B):
        r, c = i // ncols, i % ncols
        grid[:, r * H:(r + 1) * H, c * W:(c + 1) * W] = images[i]
    return grid


# =============================================================================
# Sample from saved model
# =============================================================================

def sample_mode(args):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model from {args.model}...")
    model = LogoUNet(img_ch=3, base_ch=args.base_ch).to(device)
    model.load_state_dict(torch.load(args.model, map_location=device))
    model.eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model: {n_params:,} params")

    beta, alpha_bar = make_beta_schedule(T=args.timesteps)
    beta = beta.to(device)
    alpha_bar = alpha_bar.to(device)

    os.makedirs(args.out_dir, exist_ok=True)

    for i in range(args.n_batches):
        save_path = os.path.join(args.out_dir, f'logos_{i+1:03d}.png')
        generate_samples(model, device, beta, alpha_bar, args, save_path=save_path, n=args.n)
    print(f"Generated {args.n_batches * args.n} logos in {args.out_dir}/")


# =============================================================================
# CLI
# =============================================================================

def smoke_test(args):
    """Quick test with synthetic data to verify the pipeline works."""
    import tempfile, random, numpy as np

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")
    print("Generating 20 synthetic test images...")

    tmpdir = tempfile.mkdtemp()
    for i in range(20):
        img = Image.new('RGB', (128, 128),
                        color=random.choice(['#FF6B6B', '#4ECDC4', '#45B7D1',
                                              '#96CEB4', '#FFEAA7', '#DDA0DD']))
        draw = ImageDraw.Draw(img)
        for _ in range(random.randint(1, 3)):
            x, y = random.randint(10, 118), random.randint(10, 118)
            r = random.randint(15, 40)
            color = random.choice(['#FFF', '#000', '#2C3E50', '#E74C3C'])
            shape = random.choice(['circle', 'rect'])
            if shape == 'circle':
                draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
            else:
                draw.rectangle([x, y, x+r, y+r], fill=color)
        img.save(os.path.join(tmpdir, f"test_{i:03d}.png"))

    # Quick train
    os.makedirs(args.out_dir, exist_ok=True)
    ds = LogoDataset(tmpdir, image_size=args.image_size)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True)
    print(f"  Synthetic images: {len(ds)}")

    model = LogoUNet(img_ch=3, base_ch=args.base_ch).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  Model: {n_params:,} params")

    beta, alpha_bar = make_beta_schedule(T=args.timesteps)
    beta, alpha_bar = beta.to(device), alpha_bar.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)

    print(f"  Running {args.max_steps} steps...")
    model.train()
    for step in range(args.max_steps):
        for x in dl:
            if step >= args.max_steps:
                break
            x = x.to(device)
            B = x.shape[0]
            t = torch.randint(0, args.timesteps, (B,), device=device)
            noise = torch.randn_like(x)
            a_bar = alpha_bar[t].view(B, 1, 1, 1)
            x_t = torch.sqrt(a_bar) * x + torch.sqrt(1 - a_bar) * noise
            pred = model(x_t, t)
            loss = F.mse_loss(pred, noise)
            opt.zero_grad()
            loss.backward()
            opt.step()
            step += 1
            if step % max(1, args.max_steps // 4) == 0:
                print(f"  Step {step:4d} | loss {loss.item():.6f}")

    print(f"  Final loss: {loss.item():.6f}")
    # Generate 4 test samples
    sample_path = os.path.join(args.out_dir, 'smoke_test.png')
    generate_samples(model, device, beta, alpha_bar, args, save_path=sample_path, n=4)
    print(f"\nPipeline OK. Smoke test samples -> {sample_path}")
    print("Ready for real training.")


def main():
    parser = argparse.ArgumentParser(description="LogoGen: small logo diffusion model")
    sub = parser.add_subparsers(dest='cmd')

    p_smoke = sub.add_parser('smoke', help='Quick smoke test with synthetic data')
    p_smoke.add_argument('--out-dir', type=str, default='/content/logogen_test')
    p_smoke.add_argument('--image-size', type=int, default=128)
    p_smoke.add_argument('--batch-size', type=int, default=16)
    p_smoke.add_argument('--max-steps', type=int, default=200)
    p_smoke.add_argument('--lr', type=float, default=2e-4)
    p_smoke.add_argument('--timesteps', type=int, default=1000)
    p_smoke.add_argument('--base-ch', type=int, default=64)

    p_train = sub.add_parser('train', help='Train on a directory of logos')
    p_train.add_argument('--image-dir', type=str, required=True)
    p_train.add_argument('--out-dir', type=str, default='/content/logogen')
    p_train.add_argument('--image-size', type=int, default=128)
    p_train.add_argument('--epochs', type=int, default=50)
    p_train.add_argument('--max-steps', type=int, default=50000)
    p_train.add_argument('--batch-size', type=int, default=16)
    p_train.add_argument('--lr', type=float, default=2e-4)
    p_train.add_argument('--timesteps', type=int, default=1000)
    p_train.add_argument('--base-ch', type=int, default=64)

    p_sample = sub.add_parser('sample', help='Generate logos from saved model')
    p_sample.add_argument('--model', type=str, required=True)
    p_sample.add_argument('--out-dir', type=str, default='/content/logogen_output')
    p_sample.add_argument('--n', type=int, default=8)
    p_sample.add_argument('--n-batches', type=int, default=5)
    p_sample.add_argument('--image-size', type=int, default=128)
    p_sample.add_argument('--timesteps', type=int, default=1000)
    p_sample.add_argument('--base-ch', type=int, default=64)

    args = parser.parse_args()
    if args.cmd == 'train':
        train(args)
    elif args.cmd == 'sample':
        sample_mode(args)
    elif args.cmd == 'smoke':
        smoke_test(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
