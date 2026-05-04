## What Is an End-to-End Fine-Tuning Pipeline?

**The Problem:**
You have a pre-trained model that understands language but cannot solve your specific task. You have a dataset of labeled examples. But putting these together is not just "call model.fit()." A real pipeline requires data loading, tokenization, train/val/test splits, a training loop with logging, checkpointing, evaluation, and model saving. How do you wire all these pieces together into a production-ready system?

**Definition:**
An **end-to-end fine-tuning pipeline** is the complete workflow from raw data and a pre-trained model to a trained, evaluated, and saved model ready for deployment. It includes data preparation, training with proper optimization and regularization, validation monitoring, checkpoint persistence, and final evaluation.

**Real-life analogy:**
A fine-tuning pipeline is like a professional kitchen. The pre-trained model is a chef who already knows how to cook. Your dataset is a crate of local ingredients. The pipeline is the entire kitchen operation: prep station (tokenization), recipe execution (training loop), taste-testing (validation), food photography (evaluation), and packaging for delivery (model saving). A home cook might just throw ingredients in a pan. A professional kitchen has stations, timers, quality checks, and documentation.

**Tiny numeric example:**
Zero-shot DistilBERT on IMDB (5000 train, 1000 test):
- Before fine-tuning: 50.2% accuracy (random guessing)
- After 3 epochs of fine-tuning: 87.4% accuracy
- The pipeline added 37.2 percentage points of accuracy by teaching the model the specific patterns of movie review sentiment.

**Common confusion:**
- **"Fine-tuning is just calling .fit() on the model."** No. Real fine-tuning requires learning rate scheduling, gradient clipping, mixed precision, checkpointing, and distributed training. The .fit() call hides all of this.
- **"You should always fine-tune all parameters."** No. For large models, full fine-tuning is often too expensive. Techniques like LoRA fine-tune only 0.1% of parameters and can match full fine-tuning.
- **"More epochs is always better."** No. Without early stopping, models overfit. Validation loss typically decreases then increases; you should save the checkpoint at minimum validation loss.
- **"Checkpoints are just for resuming."** They are also for ensembling (average multiple checkpoints), for ablation studies (compare epoch 1 vs epoch 5), and for safe deployment (roll back if the new model is worse).
- **"You only need train and test sets."** A validation set is essential for hyperparameter tuning and early stopping. Testing on the test set during training leaks information and invalidates your final metrics.
- **"Fine-tuning fixes all problems."** Fine-tuning teaches the model a specific task distribution. It does not fix hallucination, bias, or safety issues from pre-training. Those require alignment techniques.

**Where it appears in our code:**
`src/phase151/phase151_fine_tuning_pipeline.py` — The complete pipeline: load DistilBERT, load IMDB, tokenize, train for 3 epochs with AdamW and linear warmup, save checkpoints, evaluate zero-shot vs fine-tuned accuracy, and plot the comparison.
