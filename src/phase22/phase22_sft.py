#!/usr/bin/env python3
"""
================================================================================
Phase 22: Supervised Fine-Tuning — From Text Generator to Helpful Assistant
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 21, we trained a GPT that generates text.
But it doesn't answer questions helpfully.

Pre-trained GPT on "What is 2+2?" might say:
  "What is 2+2? That is an interesting mathematical question..."

Fine-tuned GPT should say:
  "4"

SFT teaches the model the FORMAT of being helpful.
We show it thousands of (instruction, response) pairs.

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# SYNTHETIC INSTRUCTION DATASET
# ==============================================================================

def create_instruction_dataset():
    """
    Create a tiny synthetic instruction-following dataset.

    Each example is: (instruction, response)
    The model learns to map instructions to appropriate responses.
    """
    dataset = [
        ("What is 2+2?", "4"),
        ("What is the capital of France?", "Paris"),
        ("What color is the sky?", "Blue"),
        ("How many days in a week?", "7"),
        ("What is 5*6?", "30"),
        ("Name a primary color.", "Red"),
        ("What is 10-3?", "7"),
        ("What planet do we live on?", "Earth"),
        ("What is 8/2?", "4"),
        ("How many sides does a triangle have?", "3"),
        ("What is 3+5?", "8"),
        ("What is the opposite of hot?", "Cold"),
        ("What is 9*9?", "81"),
        ("Name a vowel.", "A"),
        ("What is 100-50?", "50"),
    ]

    return dataset


# ==============================================================================
# DEMONSTRATION: Before and After SFT
# ==============================================================================

def demonstrate_sft():
    """Show the difference between pre-trained and fine-tuned behavior."""
    print("=" * 60)
    print("SUPERVISED FINE-TUNING DEMONSTRATION")
    print("=" * 60)
    print()

    dataset = create_instruction_dataset()

    print("  Training Data (Instruction -> Response):")
    print()
    for instruction, response in dataset:
        print(f"    Instruction: '{instruction}'")
        print(f"    Response:    '{response}'")
        print()

    print("  " + "-" * 56)
    print()
    print("  BEFORE SFT (Pre-trained GPT behavior):")
    print("    Input: 'What is 2+2?'")
    print("    Output: 'What is 2+2? That is an interesting question...'")
    print("    -> The model just COMPLETES the text, doesn't answer")
    print()

    print("  AFTER SFT (Fine-tuned behavior):")
    print("    Input: 'What is 2+2?'")
    print("    Output: '4'")
    print("    -> The model ANSWERS the question concisely")
    print()

    print("  What changed?")
    print("    The model learned a PATTERN:")
    print("      Question -> Short Answer")
    print("    Not:")
    print("      Question -> Continuation of question")
    print()


# ==============================================================================
# SFT PROCESS VISUALIZATION
# ==============================================================================

def visualize_sft_process():
    """Visualize the SFT pipeline."""
    print("=" * 60)
    print("THE SFT PIPELINE")
    print("=" * 60)
    print()

    print("  Step 1: PRE-TRAINING")
    print("    Data: Internet text (books, websites, Wikipedia)")
    print("    Task: Predict next token")
    print("    Result: GPT can generate text")
    print("    Problem: Doesn't follow instructions")
    print()

    print("  Step 2: CREATE INSTRUCTION DATASET")
    print("    Collect pairs: (instruction, response)")
    print("    Example: ('What is 2+2?', '4')")
    print("    Format: Add system prompt + user/assistant tags")
    print()

    print("  Step 3: FINE-TUNING")
    print("    Train GPT on instruction dataset")
    print("    Loss: Cross-entropy on response tokens")
    print("    Only update model weights slightly")
    print("    Keep pre-trained knowledge intact")
    print()

    print("  Step 4: EVALUATION")
    print("    Test on unseen instructions")
    print("    Check: Is the response helpful? Accurate? Safe?")
    print()

    print("  Result: A helpful assistant!")
    print()


# ==============================================================================
# CATASTROPHIC FORGETTING DEMONSTRATION
# ==============================================================================

def demonstrate_catastrophic_forgetting():
    """Show the risk of losing pre-trained knowledge during fine-tuning."""
    print("=" * 60)
    print("CATASTROPHIC FORGETTING")
    print("=" * 60)
    print()

    print("  Risk: If we fine-tune too aggressively,")
    print("        the model might FORGET pre-trained knowledge.")
    print()

    print("  Example:")
    print("    Pre-trained GPT knows: 'Shakespeare wrote Hamlet'")
    print()
    print("    After fine-tuning ONLY on math questions:")
    print("      User: 'Who wrote Hamlet?'")
    print("      Assistant: '42'  <- FORGOTTEN!")
    print()

    print("  Solutions:")
    print("    1. Low learning rate (small weight updates)")
    print("    2. Mix instruction data with pre-training data")
    print("    3. LoRA (Low-Rank Adaptation) — only update small adapters")
    print()

    print("  Analogy:")
    print("    A pianist learns jazz. If they ONLY practice jazz")
    print("    for months, they might forget classical pieces.")
    print("    Solution: Practice both, or add jazz as a 'layer'")
    print("    on top of classical skills.")
    print()


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def visualize_sft():
    """Create a visualization of the SFT process."""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Title
    ax.text(0.5, 0.95, 'Supervised Fine-Tuning Pipeline', ha='center', fontsize=16,
            fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightblue'))

    # Pre-trained model
    ax.text(0.2, 0.80, 'Pre-trained GPT', ha='center', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='lightyellow'))
    ax.text(0.2, 0.75, 'Can generate text\nBut not helpful', ha='center', fontsize=9, style='italic')

    # Arrow
    ax.arrow(0.3, 0.77, 0.15, 0, head_width=0.03, head_length=0.02, fc='black')

    # Instruction data
    ax.text(0.55, 0.80, 'Instruction Dataset', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax.text(0.55, 0.72, '(Q: What is 2+2?, A: 4)\n(Q: Capital of France?, A: Paris)',
            ha='center', fontsize=8, family='monospace')

    # Arrow down
    ax.arrow(0.55, 0.68, 0, -0.08, head_width=0.03, head_length=0.02, fc='black')

    # Fine-tuning
    ax.text(0.55, 0.55, 'Fine-Tuning\n(Low LR, few epochs)', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightcoral'))

    # Arrow down
    ax.arrow(0.55, 0.50, 0, -0.08, head_width=0.03, head_length=0.02, fc='black')

    # Fine-tuned model
    ax.text(0.55, 0.35, 'Fine-tuned Assistant', ha='center', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='plum'))
    ax.text(0.55, 0.28, 'Follows instructions\nAnswers helpfully', ha='center', fontsize=9, style='italic')

    # Warning
    ax.text(0.85, 0.55, 'WARNING:\nCatastrophic\nForgetting', ha='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='salmon'))
    ax.arrow(0.75, 0.55, -0.08, 0, head_width=0.03, head_length=0.02, fc='red')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase22/sft_pipeline.png', dpi=150)
    print("Plot saved to: src/phase22/sft_pipeline.png")
    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 22: SUPERVISED FINE-TUNING")
    print("=" * 60)
    print()
    print("  Goal: Turn a text generator into a helpful assistant")
    print()

    # Demonstrate SFT
    demonstrate_sft()

    # Show pipeline
    visualize_sft_process()

    # Show catastrophic forgetting
    demonstrate_catastrophic_forgetting()

    # Visualize
    visualize_sft()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Synthetic instruction dataset")
    print("    - SFT pipeline demonstration")
    print("    - Before/after comparison")
    print("    - Catastrophic forgetting explanation")
    print()
    print("  KEY INSIGHT:")
    print("    SFT teaches the FORMAT of being helpful.")
    print("    It does NOT teach new facts.")
    print("    It teaches: 'When you see a question, answer it.'")
    print()
    print("  THE SFT PIPELINE:")
    print("    1. Pre-train GPT on internet text")
    print("    2. Collect (instruction, response) pairs")
    print("    3. Fine-tune GPT with low learning rate")
    print("    4. Evaluate on unseen instructions")
    print()
    print("  NEXT QUESTION:")
    print("    'SFT teaches format, but models can still")
    print("     produce harmful outputs. How do we align")
    print("     them with human values?'")
    print("=" * 60)
