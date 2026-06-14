# CortexCode Colab Guide

> The cleanest way to train and use CortexCode is from a Colab notebook that pulls the code from GitHub. This file explains the workflow.

## The 3-step workflow

### Step 1: Create a new Colab notebook
Go to https://colab.research.google.com, click "New notebook".

### Step 2: Enable GPU
`Runtime` → `Change runtime type` → set Hardware accelerator to **T4 GPU** → Save.

### Step 3: Run these cells in order

**Cell 1: Get the code**
```python
!git clone https://github.com/srivtx/ai-miden.git
%cd ai-miden/cortexcode
```

**Cell 2: Upload your codebase**
Two options:

*Option A*: Drag-and-drop a folder of `.py` files into the left sidebar, then run:
```python
import os
os.makedirs("/content/codebase", exist_ok=True)
# Then drag your .py files into /content/codebase/ via the file browser
```

*Option B*: Clone from a different git repo:
```python
!git clone https://github.com/your_name/your_repo.git /content/codebase
```

*Option C*: Use a small built-in test set (the gm/ curriculum from this repo):
```python
import shutil
shutil.copytree("/content/ai-miden/docs/gm", "/content/codebase")
```

**Cell 3: Train (1-2 hours on T4)**
```python
!python cortexcode_torch.py train \
    --data-dir /content/codebase \
    --steps 2000 \
    --batch-size 16 \
    --dim 256 \
    --n-layers 4 \
    --out /content/cortexcode.pt
```

**Cell 4: Sample**
```python
!python cortexcode_torch.py sample \
    --prompt "def my_function(" \
    --n-tokens 100 \
    --model /content/cortexcode.pt
```

**Cell 5: Save to Drive (so the model survives Colab restarts)**
```python
from google.colab import drive
drive.mount('/content/drive')
!cp /content/cortexcode.pt /content/drive/MyDrive/cortexcode.pt
print("Model saved to Drive.")
```

## That's it

The full pipeline is 4 cells. Total time: 1-2 hours for training + 5 minutes for the rest.

## Troubleshooting

**`No module named cortexcode_torch`**: Make sure you ran the `cd` command in Cell 1.

**`CUDA out of memory`**: Reduce `--batch-size 8` or `--dim 192`.

**`RuntimeError: Found no files at /content/codebase`**: Upload some `.py` files first.

**`Output looks like gibberish after 30 min`**: Train longer (`--steps 5000`) or use a larger codebase.

**`Can't find a GPU`**: Runtime → Change runtime type → T4 GPU.

## What the code does

See `cortexcode.py` (NumPy demo, no GPU needed) and `cortexcode_torch.py` (PyTorch trainer, GPU recommended). Both implement all 5 MSPCH features from the `nature/` curriculum:

1. Multi-system memory (slow transformer + fast key-value)
2. Replay consolidation (sleep-driven)
3. Neuromodulator gating (DA modulates attention)
4. Homeostatic plasticity (Turrigiano scaling)
5. Variational surprise (cosine similarity for retrieval)
