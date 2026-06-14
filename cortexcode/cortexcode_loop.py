"""
CortexCode Loop: continuous learning architecture
=================================================

A self-improving code model. Unlike a static LLM, this system:

    1. WATCH  - polls a directory for new/changed .py files
    2. CURATE - scores each file by surprise (model's prediction error)
    3. LEARN  - one online SGD step on high-surprise files
    4. SLEEP  - replay-based consolidation every N edits

This is the Multi-Scale Predictive Coding Hypothesis (MSPCH) in code:
- Slow weights = the transformer (consolidated knowledge)
- Fast memory = deque of recent surprising examples
- Replay buffer = older examples, used to prevent forgetting
- Surprise gate = only learn when model is uncertain

Run modes:

    # 1. Pre-train (uses existing model from cortexcode_torch.py)
    !python cortexcode_loop.py pretrain \\
        --data-dir /content/codebase \\
        --base-model /content/cortexcode.pt \\
        --out /content/cortexcode_loop.pt \\
        --steps 1000

    # 2. Test the loop with a simulated stream of new code
    !python cortexcode_loop.py test \\
        --model /content/cortexcode_loop.pt \\
        --n-examples 50

    # 3. Run the loop live on a directory
    !python cortexcode_loop.py watch \\
        --model /content/cortexcode_loop.pt \\
        --dir /content/codebase

    # 4. Pull from the internet and learn from trending Python repos
    !python cortexcode_loop.py learn-internet \\
        --model /content/cortexcode.pt \\
        --out /content/cortexcode_loop.pt \\
        --n-repos 3

The test mode is what you run in Colab to see the loss go DOWN over time.
The learn-internet mode pulls real GitHub repos, clones them, and feeds
the code to the loop. This is the "auto learn from online" wedge.
"""

import os
import time
import json
import random
import argparse
import threading
import tempfile
import subprocess
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import deque
from typing import Optional, List, Tuple

import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from cortexcode_torch import (
    CortexCodeModel, CodeTokenizer, load_python_files, CodeDataset,
)


# =============================================================================
# The Loop
# =============================================================================

class CortexCodeLoop:
    """
    A 4-component continual learning system.

    The slow weights (transformer) are loaded once and updated online.
    The fast memory is a deque of recent surprising examples.
    The replay buffer is older examples used during sleep to prevent forgetting.
    """

    def __init__(self, model, tokenizer, lr=1e-5, surprise_threshold=2.0,
                 replay_size=2000, sleep_every=20, sleep_steps=10,
                 device='cuda'):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.lr = lr
        self.surprise_threshold = surprise_threshold
        self.sleep_every = sleep_every
        self.sleep_steps = sleep_steps
        self.device = device

        self.optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

        # MSPCH memory systems
        self.fast_memory = deque(maxlen=200)         # last 200 surprising examples
        self.replay_buffer = deque(maxlen=replay_size)  # all-time, for sleep

        # Tracking
        self.edit_count = 0
        self.sleep_count = 0
        self.skipped_boring = 0
        self.skipped_short = 0
        self.loss_history = []   # list of (edit_index, kind, loss)
        self.surprise_log = []   # list of (edit_index, surprise_loss)

    # ----- 1. WATCH / scoring -----

    def compute_surprise(self, text):
        """Loss of model on text = how surprising it is. Lower = more expected."""
        self.model.eval()
        ids = self.tokenizer.encode(text)
        if len(ids) < 10:
            return None
        with torch.no_grad():
            x = torch.tensor([ids[:-1]], device=self.device)
            y = torch.tensor([ids[1:]], device=self.device)
            _, loss = self.model(x, y)
        return loss.item()

    # ----- 2. CURATE / single update -----

    def learn_step(self, text, weight=1.0):
        """One online SGD step on a single text."""
        self.model.train()
        ids = self.tokenizer.encode(text)
        if len(ids) < 10:
            return None
        # Truncate to max_seq_len
        ids = ids[:self.model.max_seq_len + 1]
        x = torch.tensor([ids[:-1]], device=self.device)
        y = torch.tensor([ids[1:]], device=self.device)
        _, loss = self.model(x, y)
        self.optimizer.zero_grad()
        (loss * weight).backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        return loss.item()

    def on_new_text(self, text, source="watch"):
        """Main entry point. Returns dict describing what happened."""
        surprise = self.compute_surprise(text)
        result = {'source': source, 'surprise': surprise, 'action': None}

        if surprise is None:
            self.skipped_short += 1
            result['action'] = 'skip'
            result['reason'] = 'too_short'
            return result

        if surprise < self.surprise_threshold:
            self.skipped_boring += 1
            result['action'] = 'skip'
            result['reason'] = 'boring'
            return result

        # Surprising enough to learn
        self.fast_memory.append((text, surprise))
        self.replay_buffer.append((text, surprise))
        self.surprise_log.append((self.edit_count, surprise))

        new_loss = self.learn_step(text)
        self.loss_history.append((self.edit_count, 'online', new_loss))
        self.edit_count += 1
        result['action'] = 'learn'
        result['new_loss'] = new_loss

        # Sleep periodically
        if self.edit_count > 0 and self.edit_count % self.sleep_every == 0:
            sleep_loss = self.sleep_cycle()
            result['sleep_loss'] = sleep_loss
            result['sleep_count'] = self.sleep_count

        return result

    # ----- 3. SLEEP / consolidation -----

    def sleep_cycle(self):
        """Replay mix of recent + old to consolidate. Prevents forgetting."""
        self.sleep_count += 1
        if not self.replay_buffer:
            return None
        losses = []
        n = min(self.sleep_steps, len(self.replay_buffer))
        for _ in range(n):
            # 50% fast memory (recent), 50% replay buffer (older)
            if self.fast_memory and random.random() < 0.5:
                text, _ = random.choice(list(self.fast_memory))
            else:
                text, _ = random.choice(list(self.replay_buffer))
            # Half weight for replay (less aggressive update)
            loss = self.learn_step(text, weight=0.5)
            if loss is not None:
                losses.append(loss)
        if not losses:
            return None
        mean_loss = sum(losses) / len(losses)
        self.loss_history.append((self.edit_count, 'sleep', mean_loss))
        return mean_loss

    # ----- 4. WATCH / polling -----

    def watch_directory(self, directory, interval=0.5, max_iterations=None,
                        verbose=True):
        """Poll a directory for changed .py files. Block forever or until max."""
        directory = Path(directory)
        last_mtime = {}

        # First pass: snapshot existing files (don't learn from pre-existing)
        for path in directory.rglob("*.py"):
            if "__pycache__" in str(path) or "/.git/" in str(path):
                continue
            try:
                last_mtime[str(path)] = path.stat().st_mtime
            except OSError:
                pass

        if verbose:
            print(f"Watching {directory} (Ctrl+C to stop)...")

        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            for path in directory.rglob("*.py"):
                if "__pycache__" in str(path) or "/.git/" in str(path):
                    continue
                key = str(path)
                try:
                    mtime = path.stat().st_mtime
                except OSError:
                    continue
                if key in last_mtime and last_mtime[key] != mtime:
                    # File changed
                    try:
                        text = path.read_text(errors='ignore')
                        result = self.on_new_text(text, source=f"file:{path.name}")
                        if verbose and result['action'] == 'learn':
                            self._log_result(result)
                    except Exception as e:
                        if verbose:
                            print(f"  Error reading {path}: {e}")
                last_mtime[key] = mtime

            iteration += 1
            time.sleep(interval)

    def _log_result(self, result):
        msg = (f"[edit {self.edit_count:4d}] LEARN  "
               f"surprise={result['surprise']:.3f}  loss={result['new_loss']:.3f}")
        if 'sleep_loss' in result:
            msg += f"  | SLEEP #{result['sleep_count']}  loss={result['sleep_loss']:.3f}"
        print(msg)

    # ----- simulated stream (for testing) -----

    def run_simulated_stream(self, texts, delay=0.0, verbose=True):
        """Feed a list of texts as if they were incoming edits."""
        for i, text in enumerate(texts):
            result = self.on_new_text(text, source=f"sim:{i}")
            if verbose and result['action'] == 'learn':
                self._log_result(result)
            if delay > 0:
                time.sleep(delay)
        return self._summary()

    def run_internet_stream(self, n_repos=3, max_files_per_repo=30,
                            verbose=True, fetcher=None):
        """Pull repos from the internet and feed to the loop."""
        if fetcher is None:
            fetcher = InternetFetcher()
        repos = fetcher.fetch_github_trending(n_repos)
        for repo_url in repos:
            if verbose:
                print(f"\n--- Fetching {repo_url} ---")
            count = 0
            for text in fetcher.clone_and_extract(repo_url):
                if count >= max_files_per_repo:
                    break
                result = self.on_new_text(text, source=f"internet:{repo_url.split('/')[-1]}")
                count += 1
                if verbose and result['action'] == 'learn':
                    self._log_result(result)
            if verbose:
                print(f"  processed {count} files from {repo_url}")
        return self._summary()

    # ----- save / load / plot -----

    def save(self, path):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'tokenizer': {
                'token_to_id': self.tokenizer.token_to_id,
                'id_to_token': self.tokenizer.id_to_token,
                'next_id': self.tokenizer.next_id,
            },
            'config': {
                'dim': self.model.dim, 'n_layers': self.model.n_layers,
                'n_heads': self.model.n_heads, 'ffn_dim': self.model.ffn_dim,
                'max_seq_len': self.model.max_seq_len,
            },
            'loop_state': {
                'edit_count': self.edit_count,
                'sleep_count': self.sleep_count,
                'skipped_boring': self.skipped_boring,
                'skipped_short': self.skipped_short,
                'loss_history': self.loss_history,
                'surprise_log': self.surprise_log,
            },
        }, path)
        print(f"Saved loop model to {path}")

    def _summary(self):
        return {
            'edit_count': self.edit_count,
            'sleep_count': self.sleep_count,
            'skipped_boring': self.skipped_boring,
            'skipped_short': self.skipped_short,
            'fast_memory_size': len(self.fast_memory),
            'replay_buffer_size': len(self.replay_buffer),
        }

    def plot_loss_curve(self, save_path):
        """Render the loss curve: online updates (red) + sleep cycles (black squares)."""
        if not self.loss_history:
            print("No loss history to plot.")
            return
        edits = [e for e, _, _ in self.loss_history]
        losses = [l for _, _, l in self.loss_history]
        types = [t for _, t, _ in self.loss_history]

        online_x = [e for e, t in zip(edits, types) if t == 'online']
        online_y = [l for l, t in zip(losses, types) if t == 'online']
        sleep_x = [e for e, t in zip(edits, types) if t == 'sleep']
        sleep_y = [l for l, t in zip(losses, types) if t == 'sleep']

        fig, ax = plt.subplots(figsize=(12, 6))
        if online_x:
            ax.plot(online_x, online_y, 'o-', alpha=0.4, color='#c84a2e',
                    label=f'online update (n={len(online_x)})', markersize=4)
        if sleep_x:
            ax.plot(sleep_x, sleep_y, 's-', color='#191712', markersize=12,
                    linewidth=2, label=f'sleep consolidation (n={len(sleep_x)})')

        # Rolling average of online updates
        if len(online_x) > 10:
            window = max(5, len(online_x) // 20)
            rolling = []
            for i in range(len(online_x)):
                start = max(0, i - window + 1)
                rolling.append(sum(online_y[start:i+1]) / (i - start + 1))
            ax.plot(online_x, rolling, '-', color='#c84a2e', linewidth=2.5,
                    label=f'online rolling avg (window={window})')

        ax.set_xlabel('Edit #', fontsize=12)
        ax.set_ylabel('Loss', fontsize=12)
        ax.set_title('CortexCode Loop: online learning + sleep consolidation',
                     fontsize=14)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=100)
        plt.close()
        print(f"Loss curve saved to {save_path}")


# =============================================================================
# Loading a saved loop model
# =============================================================================

def load_loop_model(path, device='cuda'):
    """Load a saved loop model. Returns (model, tokenizer, loop_state)."""
    ckpt = torch.load(path, map_location=device, weights_only=False)
    cfg = ckpt['config']
    tok_data = ckpt['tokenizer']

    tokenizer = CodeTokenizer()
    tokenizer.token_to_id = tok_data['token_to_id']
    tokenizer.id_to_token = {int(k): v for k, v in tok_data['id_to_token'].items()}
    tokenizer.next_id = tok_data['next_id']

    model = CortexCodeModel(
        vocab_size=len(tokenizer), dim=cfg['dim'], n_layers=cfg['n_layers'],
        n_heads=cfg['n_heads'], ffn_dim=cfg['ffn_dim'], max_seq_len=cfg['max_seq_len']
    ).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    loop_state = ckpt.get('loop_state', {})
    return model, tokenizer, loop_state


# =============================================================================
# Internet fetcher
# =============================================================================

class InternetFetcher:
    """Pulls Python code from public sources on the internet.

    No API keys needed. Uses:
    - GitHub REST API (no auth, just User-Agent header) for trending repos
    - PyPI RSS feed for new package releases
    - Hacker News API for top stories (we don't use the text yet, just signal)
    """

    def __init__(self, timeout=15, user_agent='CortexCode-Loop/0.1'):
        self.timeout = timeout
        self.ua = user_agent

    def _get(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': self.ua})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read()

    def fetch_github_trending(self, n=5):
        """Top Python repos by recent activity, via GitHub Search API.

        Uses sort=updated to get recently-pushed repos. Filters out trivial ones
        (< 5 stars) so the loop doesn't learn from empty or spam repos.
        """
        url = ("https://api.github.com/search/repositories"
               "?q=language:python"
               "&sort=updated&order=desc&per_page=30")
        try:
            data = json.loads(self._get(url))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
            print(f"  GitHub fetch failed: {e}")
            return []
        repos = []
        for item in data.get('items', []):
            if item['stargazers_count'] < 5:
                continue
            repos.append({
                'name': item['full_name'],
                'clone_url': item['clone_url'],
                'stars': item['stargazers_count'],
                'description': (item.get('description') or '')[:80],
            })
            if len(repos) >= n:
                break
        return repos

    def fetch_pypi_recent(self, n=10):
        """Recent PyPI package names from the official RSS feed."""
        url = 'https://pypi.org/rss/updates.xml'
        try:
            data = self._get(url)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  PyPI fetch failed: {e}")
            return []
        try:
            root = ET.fromstring(data)
        except ET.ParseError as e:
            print(f"  PyPI parse failed: {e}")
            return []
        packages = []
        for item in root.findall('.//item'):
            title = (item.findtext('title') or '').strip()
            # "New version of <pkg> <version>"
            if title.startswith('New version of'):
                parts = title.split()
                if len(parts) >= 4:
                    packages.append(parts[3])
            if len(packages) >= n:
                break
        return packages

    def clone_and_extract(self, repo_url, max_file_size=20000):
        """Clone a git repo to a temp dir, yield Python file contents.

        Yields tuples of (filename, text) so the loop can label the source.
        """
        with tempfile.TemporaryDirectory(prefix='cortexcode_') as tmp:
            try:
                result = subprocess.run(
                    ['git', 'clone', '--depth', '1', '--quiet', repo_url, tmp],
                    capture_output=True, timeout=60,
                )
                if result.returncode != 0:
                    print(f"  git clone failed for {repo_url}: {result.stderr.decode()[:200]}")
                    return
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"  git clone error for {repo_url}: {e}")
                return
            for path in Path(tmp).rglob('*.py'):
                spath = str(path)
                if '__pycache__' in spath or '/.git/' in spath or '/test' in spath.lower():
                    continue
                try:
                    text = path.read_text(errors='ignore')
                    if 200 <= len(text) <= max_file_size:
                        rel = spath[len(tmp) + 1:]
                        yield rel, text
                except OSError:
                    continue


# =============================================================================
# Pre-training: a few more steps to set up the loop model
# =============================================================================

def pretrain(args):
    """Train the base model a bit more, save with loop-compatible format."""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    if args.base_model and os.path.exists(args.base_model):
        print(f"Loading base model from {args.base_model}...")
        model, tokenizer, _ = load_loop_model(args.base_model, device=device)
    else:
        print("Loading data and training from scratch...")
        texts = load_python_files(args.data_dir, max_files=500)
        tokenizer = CodeTokenizer()
        tokenizer.fit(texts, min_freq=1, max_vocab=8192)
        all_tokens = []
        for t in texts:
            all_tokens.extend(tokenizer.encode(t))
        all_tokens = torch.tensor(all_tokens, dtype=torch.long)
        model = CortexCodeModel(
            vocab_size=len(tokenizer), dim=args.dim, n_layers=args.n_layers,
            n_heads=args.n_heads, ffn_dim=args.ffn_dim, max_seq_len=args.block_size,
        ).to(device)
        from torch.utils.data import DataLoader
        ds = CodeDataset(all_tokens, args.block_size)
        dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True)
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
        model.train()
        step = 0
        t0 = time.time()
        while step < args.steps:
            for x, y in dl:
                if step >= args.steps:
                    break
                x, y = x.to(device), y.to(device)
                _, loss = model(x, y)
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                step += 1
                if step % 100 == 0:
                    print(f"Step {step} | loss {loss.item():.4f} | {time.time()-t0:.1f}s")

    # Save in loop format
    loop = CortexCodeLoop(model, tokenizer, device=device)
    loop.save(args.out)


# =============================================================================
# Test mode: simulated stream of new code
# =============================================================================

SYNTHETIC_NEW_CODE = [
    # JSON parsing patterns (jc-style, similar to training)
    "def parse_json_file(path):\n    with open(path) as f:\n        data = json.load(f)\n    return data\n",
    "def process_csv(csv_path):\n    import csv\n    rows = []\n    with open(csv_path) as f:\n        reader = csv.DictReader(f)\n        for row in reader:\n            rows.append(row)\n    return rows\n",
    "def filter_dict(d, keys):\n    return {k: v for k, v in d.items() if k in keys}\n",
    "def merge_dicts(a, b):\n    result = a.copy()\n    result.update(b)\n    return result\n",
    "def flatten(nested):\n    result = []\n    for item in nested:\n        if isinstance(item, list):\n            result.extend(flatten(item))\n        else:\n            result.append(item)\n    return result\n",
    "def timestamp_to_iso(ts):\n    from datetime import datetime\n    return datetime.fromtimestamp(ts).isoformat()\n",
    "def safe_get(d, key, default=None):\n    try:\n        return d[key]\n    except (KeyError, TypeError):\n        return default\n",
    "def chunk(lst, n):\n    return [lst[i:i+n] for i in range(0, len(lst), n)]\n",
    "def unique(seq):\n    seen = set()\n    result = []\n    for item in seq:\n        if item not in seen:\n            seen.add(item)\n            result.append(item)\n    return result\n",
    "def group_by(items, key):\n    from collections import defaultdict\n    groups = defaultdict(list)\n    for item in items:\n        groups[key(item)].append(item)\n    return dict(groups)\n",
    "def parse_args():\n    import argparse\n    parser = argparse.ArgumentParser()\n    parser.add_argument('--input', required=True)\n    parser.add_argument('--output')\n    parser.add_argument('--verbose', action='store_true')\n    return parser.parse_args()\n",
    "def read_lines(path):\n    with open(path) as f:\n        return [line.rstrip('\\n') for line in f]\n",
    "def write_json(path, data):\n    import json\n    with open(path, 'w') as f:\n        json.dump(data, f, indent=2)\n",
    "def deep_get(d, keys, default=None):\n    for key in keys:\n        if isinstance(d, dict):\n            d = d.get(key, default)\n        else:\n            return default\n    return d\n",
    "def normalize_whitespace(s):\n    import re\n    return re.sub(r'\\s+', ' ', s).strip()\n",
    "def batch_process(items, func, batch_size=10):\n    results = []\n    for i in range(0, len(items), batch_size):\n        batch = items[i:i+batch_size]\n        results.extend(func(item) for item in batch)\n    return results\n",
    "def is_valid_email(email):\n    import re\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return bool(re.match(pattern, email))\n",
    "def clamp(value, lo, hi):\n    return max(lo, min(hi, value))\n",
    "def retry(func, max_attempts=3, delay=1):\n    import time\n    for attempt in range(max_attempts):\n        try:\n            return func()\n        except Exception as e:\n            if attempt == max_attempts - 1:\n                raise\n            time.sleep(delay)\n",
    "def format_bytes(n):\n    for unit in ['B', 'KB', 'MB', 'GB']:\n        if n < 1024:\n            return f'{n:.1f} {unit}'\n        n /= 1024\n    return f'{n:.1f} TB'\n",
    "def parse_duration(s):\n    import re\n    match = re.match(r'(\\d+)([smhd])', s)\n    if not match:\n        return None\n    value, unit = match.groups()\n    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}\n    return int(value) * multipliers[unit]\n",
    "def find_files(root, pattern):\n    import os\n    import fnmatch\n    matches = []\n    for dirpath, _, files in os.walk(root):\n        for f in files:\n            if fnmatch.fnmatch(f, pattern):\n                matches.append(os.path.join(dirpath, f))\n    return matches\n",
    "def memoize(func):\n    cache = {}\n    def wrapper(*args):\n        if args not in cache:\n            cache[args] = func(*args)\n        return cache[args]\n    return wrapper\n",
    "def parse_yaml(text):\n    import yaml\n    return yaml.safe_load(text)\n",
    "def to_snake_case(name):\n    import re\n    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\\1_\\2', name)\n    return re.sub(r'([a-z0-9])([A-Z])', r'\\1_\\2', s1).lower()\n",
    "def get_env(key, default=None):\n    import os\n    return os.environ.get(key, default)\n",
    "def require_env(key):\n    import os\n    value = os.environ.get(key)\n    if value is None:\n        raise RuntimeError(f'Missing required env var: {key}')\n    return value\n",
    "def truncate(s, n):\n    if len(s) <= n:\n        return s\n    return s[:n-3] + '...'\n",
    "def parse_bool(s):\n    if isinstance(s, bool):\n        return s\n    return s.lower() in ('true', 'yes', '1', 'on')\n",
    "def dedupe_preserve_order(seq):\n    seen = set()\n    return [x for x in seq if not (x in seen or seen.add(x))]\n",
    "def split_lines(s):\n    return [line for line in s.split('\\n') if line.strip()]\n",
    "def join_paths(*parts):\n    import os\n    return os.path.join(*parts)\n",
    "def basename(path):\n    import os\n    return os.path.basename(path)\n",
    "def dirname(path):\n    import os\n    return os.path.dirname(path)\n",
]


# Fix typo in synthetic data above (caught while writing)
def test_mode(args):
    """Run the loop on synthetic new code, show loss going down."""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model from {args.model}...")
    model, tokenizer, prev_state = load_loop_model(args.model, device=device)
    print(f"  prev state: {prev_state.get('edit_count', 0)} edits, "
          f"{prev_state.get('sleep_count', 0)} sleeps")

    loop = CortexCodeLoop(
        model, tokenizer, lr=args.lr, surprise_threshold=args.threshold,
        sleep_every=args.sleep_every, sleep_steps=args.sleep_steps,
        device=device,
    )

    # Run the simulated stream
    texts = SYNTHETIC_NEW_CODE * (args.n_examples // len(SYNTHETIC_NEW_CODE) + 1)
    texts = texts[:args.n_examples]
    print(f"\nFeeding {len(texts)} synthetic new-code examples...")
    print(f"  surprise_threshold = {args.threshold}")
    print(f"  sleep_every = {args.sleep_every} edits")
    print(f"  lr = {args.lr}\n")

    summary = loop.run_simulated_stream(texts, delay=0, verbose=True)
    print(f"\n--- Summary ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Save
    out_path = args.out or args.model
    loop.save(out_path)

    # Plot
    plot_path = out_path.replace('.pt', '_loss.png')
    loop.plot_loss_curve(plot_path)

    return loop, summary


# =============================================================================
# Watch mode: live directory
# =============================================================================

def watch_mode(args):
    """Run the loop on a live directory."""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model from {args.model}...")
    model, tokenizer, _ = load_loop_model(args.model, device=device)
    loop = CortexCodeLoop(
        model, tokenizer, lr=args.lr, surprise_threshold=args.threshold,
        sleep_every=args.sleep_every, sleep_steps=args.sleep_steps,
        device=device,
    )
    print(f"Watching {args.dir} (Ctrl+C to stop)...")
    try:
        loop.watch_directory(args.dir, interval=args.interval, verbose=True)
    except KeyboardInterrupt:
        print("\nStopping...")
    loop.save(args.model)
    loop.plot_loss_curve(args.model.replace('.pt', '_loss.png'))


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="CortexCode Loop: continual learning")
    sub = parser.add_subparsers(dest='cmd')

    p_pre = sub.add_parser('pretrain', help='Pre-train a model for the loop')
    p_pre.add_argument('--data-dir', type=str, default=None)
    p_pre.add_argument('--base-model', type=str, default=None)
    p_pre.add_argument('--out', type=str, required=True)
    p_pre.add_argument('--steps', type=int, default=1000)
    p_pre.add_argument('--batch-size', type=int, default=16)
    p_pre.add_argument('--block-size', type=int, default=128)
    p_pre.add_argument('--lr', type=float, default=1e-3)
    p_pre.add_argument('--dim', type=int, default=256)
    p_pre.add_argument('--n-layers', type=int, default=4)
    p_pre.add_argument('--n-heads', type=int, default=4)
    p_pre.add_argument('--ffn-dim', type=int, default=512)

    p_test = sub.add_parser('test', help='Test the loop on synthetic data')
    p_test.add_argument('--model', type=str, required=True)
    p_test.add_argument('--out', type=str, default=None)
    p_test.add_argument('--n-examples', type=int, default=50)
    p_test.add_argument('--lr', type=float, default=1e-5)
    p_test.add_argument('--threshold', type=float, default=2.0)
    p_test.add_argument('--sleep-every', type=int, default=10)
    p_test.add_argument('--sleep-steps', type=int, default=5)

    p_watch = sub.add_parser('watch', help='Watch a live directory')
    p_watch.add_argument('--model', type=str, required=True)
    p_watch.add_argument('--dir', type=str, required=True)
    p_watch.add_argument('--lr', type=float, default=1e-5)
    p_watch.add_argument('--threshold', type=float, default=2.0)
    p_watch.add_argument('--sleep-every', type=int, default=20)
    p_watch.add_argument('--sleep-steps', type=int, default=10)
    p_watch.add_argument('--interval', type=float, default=0.5)

    p_inet = sub.add_parser('learn-internet',
                            help='Pull repos from GitHub and learn from them')
    p_inet.add_argument('--model', type=str, required=True)
    p_inet.add_argument('--out', type=str, default=None)
    p_inet.add_argument('--n-repos', type=int, default=3)
    p_inet.add_argument('--max-files', type=int, default=30)
    p_inet.add_argument('--lr', type=float, default=1e-5)
    p_inet.add_argument('--threshold', type=float, default=2.0)
    p_inet.add_argument('--sleep-every', type=int, default=10)
    p_inet.add_argument('--sleep-steps', type=int, default=5)

    args = parser.parse_args()
    if args.cmd == 'pretrain':
        pretrain(args)
    elif args.cmd == 'test':
        test_mode(args)
    elif args.cmd == 'watch':
        watch_mode(args)
    elif args.cmd == 'learn-internet':
        learn_internet_mode(args)
    else:
        parser.print_help()


def learn_internet_mode(args):
    """Fetch trending Python repos from GitHub, clone, feed to loop."""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model from {args.model}...")
    model, tokenizer, _ = load_loop_model(args.model, device=device)
    loop = CortexCodeLoop(
        model, tokenizer, lr=args.lr, surprise_threshold=args.threshold,
        sleep_every=args.sleep_every, sleep_steps=args.sleep_steps,
        device=device,
    )

    fetcher = InternetFetcher()
    print(f"Fetching top {args.n_repos} Python repos from GitHub...")
    repos = fetcher.fetch_github_trending(args.n_repos)
    if not repos:
        print("No repos fetched. Check internet connection.")
        return
    for r in repos:
        print(f"  {r['name']}  ({r['stars']}*)  {r['description']}")

    print(f"\nCloning and feeding to loop (max {args.max_files} files per repo)...")
    print(f"  surprise_threshold = {args.threshold}")
    print(f"  sleep_every = {args.sleep_every} edits")
    print(f"  lr = {args.lr}\n")

    n_total = 0
    for repo in repos:
        print(f"\n--- {repo['name']} ---")
        count = 0
        for filename, text in fetcher.clone_and_extract(repo['clone_url']):
            if count >= args.max_files:
                break
            result = loop.on_new_text(text, source=f"internet:{repo['name']}/{filename}")
            count += 1
            n_total += 1
            if result['action'] == 'learn':
                loop._log_result(result)
        print(f"  processed {count} files from {repo['name']}")

    summary = loop._summary()
    print(f"\n--- Summary ---")
    print(f"  files seen: {n_total}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    out_path = args.out or args.model
    loop.save(out_path)
    loop.plot_loss_curve(out_path.replace('.pt', '_loss.png'))


if __name__ == '__main__':
    main()
