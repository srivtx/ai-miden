"""
Phase 151: Real Fine-Tuning Pipeline
=====================================
This is a REAL project. Not a toy.

We build a complete end-to-end fine-tuning pipeline:
1. Load a real pre-trained model (DistilBERT) from HuggingFace
2. Load a real dataset (IMDB sentiment classification)
3. Tokenize, split, and create PyTorch DataLoaders
4. Fine-tune the model with a proper training loop
5. Save checkpoints every epoch
6. Evaluate on a held-out test set
7. Compare accuracy before and after fine-tuning

This is exactly what AI engineers do at companies every day.
Run time: ~2-5 minutes on a CPU, ~30 seconds on a GPU.
"""

import os
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizer,
    get_linear_schedule_with_warmup,
)
from datasets import load_dataset
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================
# WHY: Centralized config makes experiments reproducible and easy to tweak.
CONFIG = {
    "model_name": "distilbert-base-uncased",
    "dataset": "imdb",
    "num_labels": 2,
    "max_length": 256,
    "batch_size": 16,
    "epochs": 3,
    "lr": 2e-5,
    "warmup_ratio": 0.1,
    "weight_decay": 0.01,
    "seed": 42,
    "output_dir": "src/phase151/checkpoints",
    "save_every": 1,  # Save checkpoint every N epochs
}

# ============================================================================
# REPRODUCIBILITY
# ============================================================================
torch.manual_seed(CONFIG["seed"])

# ============================================================================
# 1. LOAD MODEL AND TOKENIZER
# ============================================================================
# WHY: We start from a pre-trained model that already understands English.
# DistilBERT is a smaller, faster version of BERT (66M parameters).
# It was trained on BookCorpus and English Wikipedia.

print("Loading pre-trained DistilBERT...")
tokenizer = DistilBertTokenizer.from_pretrained(CONFIG["model_name"])
model = DistilBertForSequenceClassification.from_pretrained(
    CONFIG["model_name"],
    num_labels=CONFIG["num_labels"]
)

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")

# ============================================================================
# 2. LOAD AND PREPARE DATASET
# ============================================================================
# WHY: IMDB is a real-world dataset of 50,000 movie reviews labeled as
# positive or negative. It is the "Hello World" of text classification.

print(f"Loading {CONFIG['dataset']} dataset...")
raw_dataset = load_dataset(CONFIG["dataset"])

# WHY: The full IMDB dataset has 25,000 train + 25,000 test.
# For speed, we use a subset for this demo, but the code works at full scale.
train_size = 5000
test_size = 1000

def tokenize_function(examples):
    # WHY: BERT models need fixed-length input. We pad shorter sequences
    # and truncate longer ones. max_length=256 covers most reviews.
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=CONFIG["max_length"],
    )

print("Tokenizing dataset...")
tokenized_dataset = raw_dataset.map(tokenize_function, batched=True)
tokenized_dataset = tokenized_dataset.remove_columns(["text"])
tokenized_dataset = tokenized_dataset.rename_column("label", "labels")
tokenized_dataset.set_format("torch")

# Create subsets for faster training
train_subset = torch.utils.data.Subset(tokenized_dataset["train"], range(train_size))
test_subset = torch.utils.data.Subset(tokenized_dataset["test"], range(test_size))

# Split train into train/validation
val_size = int(0.1 * train_size)
train_size_real = train_size - val_size
train_dataset, val_dataset = random_split(
    train_subset, [train_size_real, val_size],
    generator=torch.Generator().manual_seed(CONFIG["seed"])
)

train_loader = DataLoader(train_dataset, batch_size=CONFIG["batch_size"], shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=CONFIG["batch_size"])
test_loader = DataLoader(test_subset, batch_size=CONFIG["batch_size"])

print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)} | Test: {len(test_subset)}")

# ============================================================================
# 3. EVALUATE BEFORE FINE-TUNING (ZERO-SHOT)
# ============================================================================
# WHY: We need a baseline. How good is the pre-trained model without any
# fine-tuning? This tells us how much value the fine-tuning adds.

def evaluate(model, dataloader, device):
    """Compute accuracy and average loss on a dataset."""
    model.eval()
    correct = 0
    total = 0
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = criterion(outputs.logits, labels)
            total_loss += loss.item()

            preds = torch.argmax(outputs.logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    avg_loss = total_loss / len(dataloader)
    return accuracy, avg_loss

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

print("\nEvaluating zero-shot (pre-trained) model...")
pre_acc, pre_loss = evaluate(model, test_loader, device)
print(f"Zero-shot Test Accuracy: {pre_acc:.4f} | Loss: {pre_loss:.4f}")

# ============================================================================
# 4. FINE-TUNING LOOP
# ============================================================================
# WHY: This is the exact loop used in production. We use AdamW (standard for
# transformers), linear learning rate warmup, and gradient accumulation.

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=CONFIG["lr"],
    weight_decay=CONFIG["weight_decay"],
)

total_steps = len(train_loader) * CONFIG["epochs"]
warmup_steps = int(total_steps * CONFIG["warmup_ratio"])
scheduler = get_linear_schedule_with_warmup(
    optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
)

os.makedirs(CONFIG["output_dir"], exist_ok=True)

train_losses = []
val_losses = []
val_accuracies = []

print("\nStarting fine-tuning...")
for epoch in range(CONFIG["epochs"]):
    model.train()
    epoch_loss = 0.0
    progress = tqdm(train_loader, desc=f"Epoch {epoch+1}/{CONFIG['epochs']}")

    for step, batch in enumerate(progress):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        # WHY: We compute loss using the model's built-in loss function,
        # which applies CrossEntropyLoss to the logits internally.
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )
        loss = outputs.loss

        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

        epoch_loss += loss.item()
        progress.set_postfix({"loss": f"{loss.item():.4f}"})

    avg_train_loss = epoch_loss / len(train_loader)
    train_losses.append(avg_train_loss)

    # Validation
    val_acc, val_loss = evaluate(model, val_loader, device)
    val_losses.append(val_loss)
    val_accuracies.append(val_acc)

    print(f"Epoch {epoch+1}: Train Loss={avg_train_loss:.4f} | Val Loss={val_loss:.4f} | Val Acc={val_acc:.4f}")

    # WHY: Checkpoints let us resume training, compare epochs, and pick the best model.
    if (epoch + 1) % CONFIG["save_every"] == 0:
        checkpoint_path = os.path.join(CONFIG["output_dir"], f"checkpoint_epoch_{epoch+1}.pt")
        torch.save({
            "epoch": epoch + 1,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "train_loss": avg_train_loss,
            "val_loss": val_loss,
            "val_acc": val_acc,
        }, checkpoint_path)
        print(f"Saved checkpoint to {checkpoint_path}")

# ============================================================================
# 5. FINAL EVALUATION
# ============================================================================
print("\nEvaluating fine-tuned model on test set...")
post_acc, post_loss = evaluate(model, test_loader, device)
print(f"Fine-tuned Test Accuracy: {post_acc:.4f} | Loss: {post_loss:.4f}")
print(f"\nImprovement: {pre_acc:.4f} -> {post_acc:.4f} (+{(post_acc-pre_acc)*100:.2f} percentage points)")

# Save final model
final_path = os.path.join(CONFIG["output_dir"], "final_model.pt")
torch.save(model.state_dict(), final_path)
print(f"Saved final model to {final_path}")

# Save metrics
metrics = {
    "zero_shot_accuracy": pre_acc,
    "zero_shot_loss": pre_loss,
    "fine_tuned_accuracy": post_acc,
    "fine_tuned_loss": post_loss,
    "improvement": post_acc - pre_acc,
    "train_losses": train_losses,
    "val_losses": val_losses,
    "val_accuracies": val_accuracies,
}
with open(os.path.join(CONFIG["output_dir"], "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

# ============================================================================
# 6. VISUALIZATION
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(range(1, CONFIG["epochs"]+1), train_losses, 'o-', label='Train Loss')
axes[0].plot(range(1, CONFIG["epochs"]+1), val_losses, 's-', label='Val Loss')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss')
axes[0].set_title('Training & Validation Loss')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].bar(['Zero-Shot', 'Fine-Tuned'], [pre_acc, post_acc], color=['coral', 'seagreen'])
axes[1].set_ylabel('Accuracy')
axes[1].set_title('Test Accuracy: Before vs After Fine-Tuning')
axes[1].set_ylim(0, 1)
for i, v in enumerate([pre_acc, post_acc]):
    axes[1].text(i, v + 0.02, f"{v:.3f}", ha='center', fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("src/phase151/fine_tuning_pipeline.png", dpi=150)
print("\nSaved visualization to src/phase151/fine_tuning_pipeline.png")

print("\n" + "="*60)
print("PHASE 151 COMPLETE")
print("="*60)
print("You have built a real fine-tuning pipeline.")
print("This is what AI engineers do every day at companies like")
print("OpenAI, Anthropic, Moonshot AI, and Google DeepMind.")
