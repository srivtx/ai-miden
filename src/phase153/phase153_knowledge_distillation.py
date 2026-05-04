"""
Phase 153: Real Knowledge Distillation
=======================================
This is a REAL project. Not a toy.

We build a complete knowledge distillation pipeline:
1. Load a real teacher model (BERT-base, 110M parameters)
2. Load a real student model (tiny BERT-style, ~14M parameters)
3. Load a real dataset (SST-2 sentiment classification)
4. Train the teacher to high accuracy on SST-2
5. Generate soft labels from the teacher with temperature scaling
6. Train the student on soft labels + hard labels
7. Train a baseline student on hard labels only
8. Compare: Teacher vs. Distilled Student vs. Baseline Student

This is how companies like Apple and Google deploy large models on phones.
Run time: ~5-10 minutes on GPU, ~15-20 minutes on CPU.
"""

import os
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import (
    BertForSequenceClassification,
    BertConfig,
    BertTokenizer,
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
CONFIG = {
    "teacher_name": "bert-base-uncased",
    "dataset": "glue",
    "subset": "sst2",
    "max_length": 128,
    "batch_size": 32,
    "epochs_teacher": 2,
    "epochs_student": 3,
    "lr": 2e-5,
    "temperature": 4.0,
    "alpha": 0.7,  # Weight for soft label loss
    "seed": 42,
    "output_dir": "src/phase153/checkpoints",
}

torch.manual_seed(CONFIG["seed"])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ============================================================================
# 1. LOAD TOKENIZER AND DATASET
# ============================================================================
print("Loading tokenizer...")
tokenizer = BertTokenizer.from_pretrained(CONFIG["teacher_name"])

print(f"Loading {CONFIG['dataset']}/{CONFIG['subset']} dataset...")
raw_dataset = load_dataset(CONFIG["dataset"], CONFIG["subset"])

# WHY: SST-2 has 67K train, 872 dev, 1821 test. We use a subset for speed.
train_subset_size = 5000
dev_subset_size = 500
test_subset_size = 1000

def tokenize_function(examples):
    return tokenizer(
        examples["sentence"],
        padding="max_length",
        truncation=True,
        max_length=CONFIG["max_length"],
    )

print("Tokenizing...")
tokenized = raw_dataset.map(tokenize_function, batched=True)
tokenized = tokenized.remove_columns(["sentence", "idx"])
tokenized = tokenized.rename_column("label", "labels")
tokenized.set_format("torch")

train_data = torch.utils.data.Subset(tokenized["train"], range(train_subset_size))
dev_data = torch.utils.data.Subset(tokenized["validation"], range(dev_subset_size))
test_data = torch.utils.data.Subset(tokenized["test"], range(test_subset_size))

train_loader = DataLoader(train_data, batch_size=CONFIG["batch_size"], shuffle=True)
dev_loader = DataLoader(dev_data, batch_size=CONFIG["batch_size"])
test_loader = DataLoader(test_data, batch_size=CONFIG["batch_size"])

print(f"Train: {len(train_data)} | Dev: {len(dev_data)} | Test: {len(test_data)}")

# ============================================================================
# 2. BUILD TEACHER MODEL
# ============================================================================
# WHY: BERT-base has 12 layers, 768 hidden dim, 110M parameters.
# We fine-tune it on SST-2 to create a strong teacher.

print("\nLoading teacher (BERT-base)...")
teacher = BertForSequenceClassification.from_pretrained(
    CONFIG["teacher_name"], num_labels=2
).to(device)

teacher_params = sum(p.numel() for p in teacher.parameters())
print(f"Teacher parameters: {teacher_params:,}")

# ============================================================================
# 3. TRAIN TEACHER
# ============================================================================
def train_model(model, loader, epochs, lr, desc="Training"):
    """Train a model and return it."""
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    total_steps = len(loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, 0, total_steps)

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        progress = tqdm(loader, desc=f"{desc} Epoch {epoch+1}/{epochs}")
        for batch in progress:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

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

            total_loss += loss.item()
            progress.set_postfix({"loss": f"{loss.item():.4f}"})

        print(f"  Epoch {epoch+1} avg loss: {total_loss/len(loader):.4f}")

    return model

def evaluate_model(model, loader):
    """Return accuracy and avg loss."""
    model.eval()
    correct = 0
    total = 0
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = criterion(outputs.logits, labels)
            total_loss += loss.item()

            preds = torch.argmax(outputs.logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    return correct / total, total_loss / len(loader)

# Train teacher
print("\nTraining teacher...")
teacher = train_model(teacher, train_loader, CONFIG["epochs_teacher"], CONFIG["lr"], "Teacher")

teacher_acc, teacher_loss = evaluate_model(teacher, test_loader)
print(f"Teacher Test Accuracy: {teacher_acc:.4f} | Loss: {teacher_loss:.4f}")

# ============================================================================
# 4. GENERATE SOFT LABELS FROM TEACHER
# ============================================================================
# WHY: Soft labels contain the teacher's confidence distribution across classes.
# This "dark knowledge" tells the student that "positive" is closer to "negative"
# than to "neutral" (though SST-2 is binary, the principle holds).

def generate_soft_labels(model, loader, temperature):
    """Generate soft targets from teacher with temperature scaling."""
    model.eval()
    soft_labels = []
    hard_labels = []
    input_ids_list = []
    attention_mask_list = []

    with torch.no_grad():
        for batch in tqdm(loader, desc="Generating soft labels"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"]

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits / temperature
            probs = torch.softmax(logits, dim=-1)

            soft_labels.append(probs.cpu())
            hard_labels.append(labels)
            input_ids_list.append(batch["input_ids"])
            attention_mask_list.append(batch["attention_mask"])

    soft_labels = torch.cat(soft_labels, dim=0)
    hard_labels = torch.cat(hard_labels, dim=0)
    input_ids = torch.cat(input_ids_list, dim=0)
    attention_mask = torch.cat(attention_mask_list, dim=0)

    return soft_labels, hard_labels, input_ids, attention_mask

print("\nGenerating soft labels from teacher...")
train_soft, train_hard, train_input_ids, train_attention_mask = generate_soft_labels(
    teacher, train_loader, CONFIG["temperature"]
)
print(f"Soft labels shape: {train_soft.shape}")

# ============================================================================
# 5. BUILD STUDENT MODEL (TINY BERT)
# ============================================================================
# WHY: The student has 4 layers instead of 12, and 256 hidden dim instead of 768.
# This is ~14M parameters vs. 110M — an 8x reduction.

print("\nBuilding student model...")
student_config = BertConfig(
    vocab_size=30522,
    hidden_size=256,
    num_hidden_layers=4,
    num_attention_heads=4,
    intermediate_size=512,
    num_labels=2,
)
student = BertForSequenceClassification(student_config).to(device)
student_params = sum(p.numel() for p in student.parameters())
print(f"Student parameters: {student_params:,} ({student_params/teacher_params*100:.1f}% of teacher)")

# ============================================================================
# 6. TRAIN STUDENT WITH DISTILLATION
# ============================================================================
# WHY: The student learns from both the teacher's soft labels (distillation)
# and the ground-truth hard labels. Alpha controls the mix.

class DistillationDataset(torch.utils.data.Dataset):
    def __init__(self, input_ids, attention_mask, soft_labels, hard_labels):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.soft_labels = soft_labels
        self.hard_labels = hard_labels

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "soft_labels": self.soft_labels[idx],
            "labels": self.hard_labels[idx],
        }

distill_dataset = DistillationDataset(train_input_ids, train_attention_mask, train_soft, train_hard)
distill_loader = DataLoader(distill_dataset, batch_size=CONFIG["batch_size"], shuffle=True)

def train_student_distilled(student, loader, epochs, lr, alpha, temperature):
    """Train student with knowledge distillation."""
    optimizer = torch.optim.AdamW(student.parameters(), lr=lr)
    total_steps = len(loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, 0, total_steps)
    ce_loss_fn = nn.CrossEntropyLoss()
    kl_loss_fn = nn.KLDivLoss(reduction="batchmean")

    student.train()
    losses = []
    for epoch in range(epochs):
        total_loss = 0.0
        progress = tqdm(loader, desc=f"Distill Epoch {epoch+1}/{epochs}")

        for batch in progress:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            soft_targets = batch["soft_labels"].to(device)
            hard_labels = batch["labels"].to(device)

            outputs = student(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits

            # Hard label loss
            hard_loss = ce_loss_fn(logits, hard_labels)

            # Soft label loss (KL divergence)
            soft_logits = logits / temperature
            soft_probs = torch.log_softmax(soft_logits, dim=-1)
            soft_targets_temp = torch.softmax(soft_targets / temperature, dim=-1)
            soft_loss = kl_loss_fn(soft_probs, soft_targets_temp) * (temperature ** 2)

            # Combined loss
            loss = alpha * soft_loss + (1 - alpha) * hard_loss

            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            total_loss += loss.item()
            progress.set_postfix({
                "loss": f"{loss.item():.4f}",
                "hard": f"{hard_loss.item():.4f}",
                "soft": f"{soft_loss.item():.4f}",
            })

        avg_loss = total_loss / len(loader)
        losses.append(avg_loss)
        print(f"  Epoch {epoch+1} avg loss: {avg_loss:.4f}")

    return student, losses

print("\nTraining student with distillation...")
student_distilled, distill_losses = train_student_distilled(
    student, distill_loader, CONFIG["epochs_student"], CONFIG["lr"],
    CONFIG["alpha"], CONFIG["temperature"]
)

distilled_acc, distilled_loss = evaluate_model(student_distilled, test_loader)
print(f"Distilled Student Test Accuracy: {distilled_acc:.4f} | Loss: {distilled_loss:.4f}")

# ============================================================================
# 7. TRAIN BASELINE STUDENT (HARD LABELS ONLY)
# ============================================================================
# WHY: We need a fair comparison. Does distillation actually help?
# Train an identical student on the same data but with hard labels only.

print("\nTraining baseline student (hard labels only)...")
student_baseline = BertForSequenceClassification(student_config).to(device)

# Convert soft-label dataset back to standard format for baseline
baseline_dataset = torch.utils.data.TensorDataset(train_input_ids, train_attention_mask, train_hard)
baseline_loader = DataLoader(baseline_dataset, batch_size=CONFIG["batch_size"], shuffle=True)

def train_baseline(model, loader, epochs, lr):
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    total_steps = len(loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, 0, total_steps)
    ce_loss_fn = nn.CrossEntropyLoss()

    model.train()
    losses = []
    for epoch in range(epochs):
        total_loss = 0.0
        progress = tqdm(loader, desc=f"Baseline Epoch {epoch+1}/{epochs}")

        for batch in progress:
            input_ids, attention_mask, labels = [b.to(device) for b in batch]
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = ce_loss_fn(outputs.logits, labels)

            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            total_loss += loss.item()
            progress.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = total_loss / len(loader)
        losses.append(avg_loss)
        print(f"  Epoch {epoch+1} avg loss: {avg_loss:.4f}")

    return model, losses

student_baseline, baseline_losses = train_baseline(
    student_baseline, baseline_loader, CONFIG["epochs_student"], CONFIG["lr"]
)

baseline_acc, baseline_test_loss = evaluate_model(student_baseline, test_loader)
print(f"Baseline Student Test Accuracy: {baseline_acc:.4f} | Loss: {baseline_test_loss:.4f}")

# ============================================================================
# 8. COMPARISON
# ============================================================================
print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Teacher (BERT-base, {teacher_params:,} params):     {teacher_acc:.4f}")
print(f"Distilled Student ({student_params:,} params):        {distilled_acc:.4f}")
print(f"Baseline Student ({student_params:,} params):         {baseline_acc:.4f}")
print(f"\nDistillation gain over baseline: {(distilled_acc - baseline_acc)*100:.2f} pp")
print(f"Student retained {(distilled_acc/teacher_acc)*100:.1f}% of teacher accuracy")

# ============================================================================
# 9. SAVE RESULTS AND VISUALIZE
# ============================================================================
os.makedirs(CONFIG["output_dir"], exist_ok=True)

metrics = {
    "teacher_accuracy": teacher_acc,
    "teacher_params": teacher_params,
    "distilled_accuracy": distilled_acc,
    "baseline_accuracy": baseline_acc,
    "student_params": student_params,
    "distillation_gain": distilled_acc - baseline_acc,
    "retention_ratio": distilled_acc / teacher_acc,
    "config": CONFIG,
}

with open(os.path.join(CONFIG["output_dir"], "distillation_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

# Save models
torch.save(student_distilled.state_dict(), os.path.join(CONFIG["output_dir"], "student_distilled.pt"))
torch.save(student_baseline.state_dict(), os.path.join(CONFIG["output_dir"], "student_baseline.pt"))

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Accuracy comparison
models = ['Teacher\n(110M)', 'Distilled\nStudent (14M)', 'Baseline\nStudent (14M)']
accs = [teacher_acc, distilled_acc, baseline_acc]
colors = ['#1f77b4', '#2ca02c', '#d62728']
bars = axes[0].bar(models, accs, color=colors)
axes[0].set_ylabel('Test Accuracy')
axes[0].set_title('Accuracy: Teacher vs. Distilled vs. Baseline')
axes[0].set_ylim(0, 1)
for bar, acc in zip(bars, accs):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{acc:.3f}", ha='center', fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='y')

# Training loss curves
axes[1].plot(range(1, len(distill_losses)+1), distill_losses, 'o-', label='Distilled', color='#2ca02c')
axes[1].plot(range(1, len(baseline_losses)+1), baseline_losses, 's-', label='Baseline', color='#d62728')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Training Loss')
axes[1].set_title('Training Loss: Distilled vs. Baseline Student')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("src/phase153/knowledge_distillation_results.png", dpi=150)
print("\nSaved visualization to src/phase153/knowledge_distillation_results.png")

print("\n" + "="*60)
print("PHASE 153 COMPLETE")
print("="*60)
print("You have distilled knowledge from a real teacher to a real student.")
print("This is how Apple ships NLP on iPhones and Google runs BERT on Search.")
