## What Is a Train-Eval Loop?

**The Problem:**
You have a model, data, and an optimizer. But training is not just one forward pass. You need to iterate over the data many times, measure performance on held-out data, adjust learning rates, and detect overfitting. A sloppy loop trains forever or stops too early. How do you structure the loop so it is correct, efficient, and informative?

**Definition:**
A **train-eval loop** is the repeating cycle of: (1) training the model for one epoch on the training set, (2) evaluating it on the validation set, (3) logging metrics, and (4) deciding whether to continue, stop, or adjust hyperparameters.

**Real-life analogy:**
A train-eval loop is like a musician preparing for a concert. Each week, they practice new pieces (training). At the end of the week, they play for their teacher (validation). The teacher gives feedback (metrics). If the musician is improving, they keep practicing. If they are getting worse, they change their technique (adjust learning rate). If they have plateaued for three weeks, they stop and pick their best performance (early stopping).

**Tiny numeric example:**
Epoch 1: Train Loss=0.52, Val Loss=0.48, Val Acc=0.78
Epoch 2: Train Loss=0.31, Val Loss=0.35, Val Acc=0.85
Epoch 3: Train Loss=0.18, Val Loss=0.29, Val Acc=0.87
Epoch 4: Train Loss=0.10, Val Loss=0.32, Val Acc=0.86  <-- Val loss increased! Overfitting.
Early stopping at epoch 3 saves the best model.

**Common confusion:**
- **"Training loss is what matters."** No. Validation loss is what matters. Training loss can decrease while validation loss increases (overfitting).
- **"You should evaluate after every batch."** That is too slow. Evaluating after every epoch is standard. For very large datasets, evaluate every N steps.
- **"The loop runs for a fixed number of epochs."** Production loops use early stopping based on validation metrics, not a fixed epoch count.
- **"Eval mode is just for testing."** You must call model.eval() during validation to disable dropout and use running batch norm statistics. Forgetting this gives incorrect validation metrics.
- **"You can skip validation to save time."** Without validation, you cannot detect overfitting or choose the best checkpoint. Validation is essential, not optional.
- **"The learning rate stays constant."** No. Learning rate schedules (warmup, decay, cosine) are critical for convergence. A constant LR often gives worse results.

**Where it appears in our code:**
`src/phase151/phase151_fine_tuning_pipeline.py` — The outer loop iterates epochs. Each epoch has an inner training loop with tqdm progress bars, followed by a validation pass. Metrics are logged and plotted after each epoch.
