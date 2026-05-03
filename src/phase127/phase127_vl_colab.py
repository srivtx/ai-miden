# FRONTIER TRACK: Phase 127 — Vision-Language Fine-tuning (LLaVA-style)
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models (llava-hf/llava-1.5-7b-hf in 4-bit)

# !pip install -q transformers datasets torch accelerate bitsandbytes matplotlib tqdm peft requests pillow

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import (
    AutoProcessor,
    AutoModelForVision2Seq,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import requests
from PIL import Image
from io import BytesIO
import gc

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# WHY: 4-bit quantization fits a 7B model into T4's 16GB VRAM.
# -----------------------------------------------------------------------------
MODEL_NAME = "llava-hf/llava-1.5-7b-hf"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
N_TRAIN_STEPS = 50
N_EVAL = 20
LR = 1e-4
MAX_NEW_TOKENS = 20

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

print(f"Loading {MODEL_NAME} ...")
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForVision2Seq.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)

# WHY: Gradient checkpointing saves memory during training.
model.gradient_checkpointing_enable()

# WHY: k-bit training prep enables gradient flow through 4-bit weights.
model = prepare_model_for_kbit_training(model)

# -----------------------------------------------------------------------------
# 2. IDENTIFY AND FREEZE EVERYTHING EXCEPT PROJECTION LAYER
# WHY: We only train the bridge between vision and language.
# -----------------------------------------------------------------------------
projector_target_modules = []
for name, module in model.named_modules():
    if "multi_modal_projector" in name and isinstance(module, torch.nn.Linear):
        projector_target_modules.append(name)
        print(f"Found projector layer: {name}")

if not projector_target_modules:
    raise ValueError("Could not find multi_modal_projector layers.")

# WHY: LoRA lets us train adapters on 4-bit weights without unquantizing.
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=projector_target_modules,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# -----------------------------------------------------------------------------
# 3. LOAD VQA DATASET
# WHY: Real image-question-answer triples teach grounded alignment.
# -----------------------------------------------------------------------------
print("Loading VQAv2 subset...")
try:
    ds = load_dataset("HuggingFaceM4/VQAv2", split="train[:500]")
    eval_ds = load_dataset("HuggingFaceM4/VQAv2", split="validation[:50]")
except Exception as e:
    print(f"Dataset load failed: {e}")
    print("Falling back to a tiny dummy dataset for demo.")
    ds = []
    eval_ds = []


def format_example(example):
    """Extract question and answer from VQAv2 format."""
    question = example.get("question", "")
    answers = example.get("answer", [])
    if isinstance(answers, list) and len(answers) > 0:
        ans = answers[0]
        if isinstance(ans, dict):
            ans = ans.get("answer", "")
        answer = str(ans)
    else:
        answer = str(answers)
    return question, answer


def get_image(example):
    """Safely extract a PIL image from the example."""
    img = example.get("image")
    if isinstance(img, Image.Image):
        return img.convert("RGB")
    return None


# Build small lists for reliable iteration
train_examples = []
if ds:
    for ex in ds:
        img = get_image(ex)
        if img is not None:
            q, a = format_example(ex)
            if q and a:
                train_examples.append((img, q, a))
        if len(train_examples) >= 500:
            break

eval_examples = []
if eval_ds:
    for ex in eval_ds:
        img = get_image(ex)
        if img is not None:
            q, a = format_example(ex)
            if q and a:
                eval_examples.append((img, q, a))
        if len(eval_examples) >= 50:
            break

print(f"Collected {len(train_examples)} train and {len(eval_examples)} eval examples.")

# -----------------------------------------------------------------------------
# 4. EVALUATION FUNCTION
# WHY: We must measure baseline accuracy before training.
# -----------------------------------------------------------------------------

def evaluate(model, examples, n_samples=None):
    model.eval()
    correct = 0
    samples = []
    n_samples = n_samples or len(examples)
    for i in tqdm(range(min(n_samples, len(examples))), desc="Evaluating"):
        img, question, answer = examples[i]
        prompt = f"USER: <image>\n{question}\nASSISTANT:"
        try:
            inputs = processor(text=prompt, images=img, return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                output = model.generate(
                    **inputs,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False,
                    pad_token_id=processor.tokenizer.pad_token_id,
                )
            gen_text = processor.decode(
                output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
            ).strip().lower()
            target = answer.strip().lower()
            is_correct = (gen_text == target) or (target in gen_text) or (gen_text in target)
            if is_correct:
                correct += 1
            if i < 3:
                samples.append((question, gen_text, target, is_correct))
        except Exception as e:
            print(f"Eval error at {i}: {e}")
        finally:
            if 'inputs' in dir():
                del inputs
            torch.cuda.empty_cache()

    accuracy = correct / min(n_samples, len(examples))
    return accuracy, samples


# -----------------------------------------------------------------------------
# 5. BASELINE EVALUATION
# -----------------------------------------------------------------------------
print("\n=== BASELINE EVALUATION ===")
if eval_examples:
    baseline_acc, baseline_samples = evaluate(model, eval_examples, n_samples=N_EVAL)
    print(f"Baseline VQA accuracy: {baseline_acc:.2%}")
    for q, gen, tgt, corr in baseline_samples:
        print(f"Q: {q}")
        print(f"A (model): {gen}")
        print(f"A (true):  {tgt}  ({'CORRECT' if corr else 'WRONG'})")
        print()
else:
    baseline_acc = 0.0
    print("No eval examples available.")

# -----------------------------------------------------------------------------
# 6. TRAINING LOOP (50 steps)
# WHY: Train only the projection adapters on real image-text pairs.
# -----------------------------------------------------------------------------
optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=LR)
training_losses = []

print("\n=== TRAINING PROJECTION LAYER ===")
model.train()
for step in range(N_TRAIN_STEPS):
    if not train_examples:
        print("No training examples. Skipping training.")
        break

    idx = np.random.randint(len(train_examples))
    img, question, answer = train_examples[idx]

    # Build full sequence prompt + answer
    prompt = f"USER: <image>\n{question}\nASSISTANT: {answer}"
    try:
        inputs = processor(text=prompt, images=img, return_tensors="pt").to(DEVICE)
        labels = inputs["input_ids"].clone()

        # WHY: Compute loss on the full sequence for simplicity.
        outputs = model(**inputs, labels=labels)
        loss = outputs.loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        training_losses.append(loss.item())
        if step % 10 == 0:
            print(f"Step {step}: loss={loss.item():.4f}")
    except Exception as e:
        print(f"Train error at step {step}: {e}")
    finally:
        if 'inputs' in dir():
            del inputs
        if 'outputs' in dir():
            del outputs
        torch.cuda.empty_cache()

# -----------------------------------------------------------------------------
# 7. POST-TRAINING EVALUATION
# -----------------------------------------------------------------------------
print("\n=== POST-TRAINING EVALUATION ===")
if eval_examples:
    post_acc, post_samples = evaluate(model, eval_examples, n_samples=N_EVAL)
    print(f"Post-training VQA accuracy: {post_acc:.2%}")
    for q, gen, tgt, corr in post_samples:
        print(f"Q: {q}")
        print(f"A (model): {gen}")
        print(f"A (true):  {tgt}  ({'CORRECT' if corr else 'WRONG'})")
        print()
else:
    post_acc = 0.0

# -----------------------------------------------------------------------------
# 8. TEST ON CUSTOM IMAGE
# WHY: Demonstrate that the trained model works on unseen real-world images.
# -----------------------------------------------------------------------------
print("Downloading custom test image...")
try:
    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
    resp = requests.get(img_url, timeout=15)
    custom_image = Image.open(BytesIO(resp.content)).convert("RGB")

    custom_question = "What animal is in this image?"
    prompt = f"USER: <image>\n{custom_question}\nASSISTANT:"
    inputs = processor(text=prompt, images=custom_image, return_tensors="pt").to(DEVICE)

    model.eval()
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=30,
            do_sample=False,
            pad_token_id=processor.tokenizer.pad_token_id,
        )
    custom_answer = processor.decode(
        output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
    ).strip()
    print(f"\nCustom image question: {custom_question}")
    print(f"Custom image answer:   {custom_answer}")
except Exception as e:
    print(f"Custom image test failed: {e}")

# -----------------------------------------------------------------------------
# 9. VISUALIZATION
# WHY: Curves make the training dynamics tangible.
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

if training_losses:
    axes[0].plot(training_losses, color='steelblue', linewidth=1.5)
axes[0].set_title('Training Loss (Projection Layer Only)')
axes[0].set_xlabel('Step')
axes[0].set_ylabel('Loss')
axes[0].grid(True, alpha=0.3)

axes[1].bar(['Baseline', 'After 50 Steps'], [baseline_acc, post_acc], color=['gray', 'forestgreen'])
axes[1].set_title('VQA Accuracy')
axes[1].set_ylabel('Accuracy')
axes[1].set_ylim(0, 1)
for i, v in enumerate([baseline_acc, post_acc]):
    axes[1].text(i, v + 0.02, f"{v:.1%}", ha='center')

plt.tight_layout()
plt.savefig('src/phase127/vl_finetuning_results.png', dpi=150)
plt.close()

print("\nPlot saved to src/phase127/vl_finetuning_results.png")

# -----------------------------------------------------------------------------
# 10. CLEANUP
# WHY: T4 memory is tight. Release everything explicitly.
# -----------------------------------------------------------------------------
gc.collect()
torch.cuda.empty_cache()
print("Done.")
