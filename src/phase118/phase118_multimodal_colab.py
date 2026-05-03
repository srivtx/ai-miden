# FRONTIER TRACK: Phase 118 — Native Multimodal Architectures (Early Fusion)
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models

# Install dependencies quietly so the user does not drown in pip logs.
!pip install -q transformers datasets torch accelerate bitsandbytes matplotlib tqdm Pillow

import os
import io
import requests
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from tqdm.auto import tqdm

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# A Wikimedia image with clear color regions and transparency (good for VQA).
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png"

# ------------------------------------------------------------------------------
# Load image
# ------------------------------------------------------------------------------
def load_image(url):
    """Download an image from URL and return a PIL Image."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content)).convert('RGB')
    return img

image = load_image(IMAGE_URL)
print(f"Loaded image: {image.size}")

# ------------------------------------------------------------------------------
# Load model: prefer LLaVA-1.5-7B in 4-bit, fallback to BLIP if OOM or missing.
# ------------------------------------------------------------------------------
use_llava = False
processor = None
model = None

try:
    from transformers import LlavaForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
    model = LlavaForConditionalGeneration.from_pretrained(
        "llava-hf/llava-1.5-7b-hf",
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    use_llava = True
    print("Successfully loaded LLaVA-1.5-7B in 4-bit.")
except Exception as e:
    print(f"LLaVA load failed ({e}). Falling back to Salesforce/blip-image-captioning-base.")
    from transformers import BlipProcessor, BlipForConditionalGeneration
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    ).to(DEVICE)
    use_llava = False

# ------------------------------------------------------------------------------
# Generation: caption and question answering
# ------------------------------------------------------------------------------
if use_llava:
    # LLaVA uses a chat template with USER/ASSISTANT roles.
    prompts = [
        "USER: <image>\nDescribe this image in one sentence.\nASSISTANT:",
        "USER: <image>\nWhat colors are prominent in this image?\nASSISTANT:",
        "USER: <image>\nIs there any transparency or see-through effect shown?\nASSISTANT:",
    ]
    for prompt_text in prompts:
        inputs = processor(text=prompt_text, images=image, return_tensors="pt").to(DEVICE)
        # Generate with a modest max length to stay fast on T4.
        output_ids = model.generate(**inputs, max_new_tokens=64, do_sample=False)
        # Decode; skip_special_tokens removes <pad> and <eos> markers.
        generated_text = processor.decode(output_ids[0], skip_special_tokens=True)
        # Remove the prompt prefix for cleaner display.
        answer = generated_text.split("ASSISTANT:")[-1].strip()
        print(f"\nPrompt: {prompt_text.replace(chr(10), ' ')}")
        print(f"Answer: {answer}")
else:
    # BLIP is simpler: image in, caption out.
    inputs = processor(image, return_tensors="pt").to(DEVICE)
    output_ids = model.generate(**inputs, max_new_tokens=50)
    caption = processor.decode(output_ids[0], skip_special_tokens=True)
    print(f"\nGenerated caption: {caption}")

# ------------------------------------------------------------------------------
# Token-level processing: show how image patches become tokens
# ------------------------------------------------------------------------------
if use_llava:
    # In LLaVA, the image is split into patches by the vision tower.
    # For a 336x336 image with patch size 14, we get 24x24 = 576 patches.
    # The processor inserts a special IMAGE_TOKEN_INDEX into the text sequence;
    # the model expands this placeholder into 576 visual tokens internally.
    dummy_prompt = "USER: <image>\nDescribe.\nASSISTANT:"
    dummy_inputs = processor(text=dummy_prompt, images=image, return_tensors="pt")
    input_ids = dummy_inputs['input_ids'][0]
    image_token_id = model.config.image_token_index
    placeholder_count = (input_ids == image_token_id).sum().item()
    print(f"\nToken-level analysis:")
    print(f"  Text sequence length (with placeholder): {len(input_ids)}")
    print(f"  Image token placeholders: {placeholder_count}")
    # The vision tower output size tells us how many patch tokens one image becomes.
    # For CLIP ViT-L/14 @ 336px: 336 / 14 = 24 patches per side -> 576 patches.
    patch_tokens_per_image = (
        model.config.vision_config.image_size // model.config.vision_config.patch_size
    ) ** 2
    print(f"  Each image becomes ~{patch_tokens_per_image} visual tokens inside the model.")
    total_in_llm = len(input_ids) - placeholder_count + patch_tokens_per_image
    print(f"  Total tokens fed to the language model: {total_in_llm}")
    print("  NOTE: This is LATE fusion — image patches pass through a separate vision encoder,")
    print("        then a projection layer, before entering the LLM.  Native early fusion would")
    print("        skip the projection and use a shared vocabulary from layer 1.")
else:
    # BLIP uses a ViT that outputs patch embeddings; the text decoder cross-attends to them.
    print("\nToken-level analysis (BLIP):")
    print("  Image is encoded by a ViT into patch embeddings.")
    print("  The text decoder uses cross-attention to these patches — a form of late fusion.")

# ------------------------------------------------------------------------------
# Late fusion demonstration: separate vision + text encoders
# ------------------------------------------------------------------------------
print("\n--- Late Fusion Demonstration ---")
from transformers import CLIPVisionModel, CLIPProcessor, GPT2Model, GPT2Tokenizer

clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_vision = CLIPVisionModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE)
gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
gpt2_text = GPT2Model.from_pretrained('gpt2').to(DEVICE)

# Vision pass: image -> ViT -> CLS vector.
clip_inputs = clip_processor(images=image, return_tensors="pt").to(DEVICE)
with torch.no_grad():
    vision_outputs = clip_vision(**clip_inputs)
vision_feature = vision_outputs.last_hidden_state[:, 0, :]  # CLS token.  (1, 768)
print(f"Vision-only feature shape: {vision_feature.shape}")

# Text pass: text -> GPT-2 -> last hidden state.
text_input = gpt2_tokenizer("A photo of", return_tensors="pt").to(DEVICE)
with torch.no_grad():
    text_outputs = gpt2_text(**text_input)
text_feature = text_outputs.last_hidden_state[:, -1, :]  # Last token.  (1, 768)
print(f"Text-only feature shape:   {text_feature.shape}")

# Late fusion = concatenation + manual projection.
late_fused = torch.cat([vision_feature, text_feature], dim=-1)  # (1, 1536)
projection = nn.Linear(1536, 768).to(DEVICE)
late_fused_projected = projection(late_fused)
print(f"Late-fused projected shape: {late_fused_projected.shape}")
print("Late fusion processes each modality separately and merges only at the end.")

# ------------------------------------------------------------------------------
# Early fusion simulation: image patches + text tokens in one transformer layer
# ------------------------------------------------------------------------------
print("\n--- Early Fusion Simulation ---")
# We simulate the core idea: take ViT patch embeddings and treat them as tokens.
from transformers import ViTModel, ViTConfig

# Use a small ViT to get patch embeddings.
vit_config = ViTConfig(
    image_size=224, patch_size=16, num_channels=3,
    hidden_size=768, num_hidden_layers=1
)
vit = ViTModel(vit_config).to(DEVICE)
# Re-use CLIP processor just for resizing and normalization.
vit_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Resize image to 224x224 and get pixel values.
pixel_values = vit_processor(
    images=image.resize((224, 224)), return_tensors="pt"
).pixel_values.to(DEVICE)
with torch.no_grad():
    vit_outputs = vit(pixel_values)
# Drop the CLS token; keep all patch tokens.
patch_embeddings = vit_outputs.last_hidden_state[:, 1:, :]  # (1, 196, 768)

# Text embeddings from GPT-2.
text_tokens = gpt2_tokenizer(
    "A photo of a transparent cube", return_tensors="pt"
).to(DEVICE)
with torch.no_grad():
    text_embeds = gpt2_text.wte(text_tokens['input_ids'])  # (1, seq_len, 768)

# Concatenate into ONE sequence — no projection layer.
combined_seq = torch.cat([text_embeds, patch_embeddings], dim=1)  # (1, seq_len+196, 768)
print(f"Combined sequence shape (early fusion): {combined_seq.shape}")

# Pass through a single transformer encoder layer — the SAME layer for both modalities.
encoder_layer = nn.TransformerEncoderLayer(
    d_model=768, nhead=8, batch_first=True
).to(DEVICE)
fused_output = encoder_layer(combined_seq)
print(f"Fused output shape: {fused_output.shape}")
print("Early fusion feeds image patches and text embeddings into the SAME layer.")

# ------------------------------------------------------------------------------
# Attention visualization (LLaVA only, best-effort)
# ------------------------------------------------------------------------------
if use_llava:
    try:
        print("\n--- Attention Visualization ---")
        prompt = "USER: <image>\nDescribe this image.\nASSISTANT:"
        inputs = processor(text=prompt, images=image, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)
        # outputs.attentions is a tuple of (layers,) each (batch, heads, seq, seq).
        last_layer_attn = outputs.attentions[-1][0].mean(dim=0).cpu().float().numpy()

        # Locate the image token placeholder in the input IDs.
        input_ids_cpu = inputs['input_ids'][0].cpu()
        placeholder_positions = (
            input_ids_cpu == model.config.image_token_index
        ).nonzero(as_tuple=True)[0]

        if len(placeholder_positions) > 0:
            placeholder_pos = placeholder_positions[0].item()
            text_len_before = placeholder_pos
            text_len_after = len(input_ids_cpu) - placeholder_pos - 1
            total_len = text_len_before + patch_tokens_per_image + text_len_after
            seq_len_attn = last_layer_attn.shape[0]

            if seq_len_attn == total_len:
                labels = (
                    [f"T{i}" for i in range(text_len_before)] +
                    [f"I{i}" for i in range(patch_tokens_per_image)] +
                    [f"T{i+text_len_before}" for i in range(text_len_after)]
                )
            else:
                # Fallback generic labels if shapes mismatch.
                labels = [f"Tok{i}" for i in range(seq_len_attn)]

            # Plot a subset so the heatmap remains readable.
            max_display = 64
            if seq_len_attn > max_display:
                start = max(0, text_len_before - 10)
                end = min(seq_len_attn, start + max_display)
                sub_attn = last_layer_attn[start:end, start:end]
                sub_labels = labels[start:end]
            else:
                sub_attn = last_layer_attn
                sub_labels = labels

            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(sub_attn, cmap='viridis', aspect='auto')
            ax.set_xticks(range(len(sub_labels)))
            ax.set_yticks(range(len(sub_labels)))
            ax.set_xticklabels(sub_labels, rotation=90, fontsize=6)
            ax.set_yticklabels(sub_labels, fontsize=6)
            ax.set_title('LLaVA Cross-Modal Attention (Last Layer, Avg Heads)')
            fig.colorbar(im, ax=ax)
            fig.tight_layout()
            fig.savefig('phase118_llava_attention.png')
            print("Saved phase118_llava_attention.png")
        else:
            print("Could not locate image placeholder for attention visualization.")
    except Exception as e:
        print(f"Attention visualization skipped due to error: {e}")

# ------------------------------------------------------------------------------
# Summary printout
# ------------------------------------------------------------------------------
print("\n" + "="*70)
print("SUMMARY: Early Fusion vs Late Fusion")
print("="*70)
print("Late Fusion (LLaVA / CLIP+GPT-2):")
print("  - Image -> Vision Encoder -> Projection -> LLM")
print("  - Text  -> Text Embedding  -------------> LLM")
print("  - Modalities merge LATE, usually only in deep LLM layers.")
print("\nEarly Fusion (Chameleon-style, simulated):")
print("  - Image -> Patch Embed -> SAME transformer as text")
print("  - Text  -> Text Embed  -> SAME transformer")
print("  - Modalities merge from layer 1; every token attends to every other.")
print("="*70)
