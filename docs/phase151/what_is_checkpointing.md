## What Is Checkpointing?

**The Problem:**
Training a large model takes hours or days on expensive GPUs. If your server crashes at epoch 49 of 50, you lose everything. If you want to compare the model at epoch 10 vs epoch 50, you need both. If you want to ensemble multiple checkpoints for better accuracy, you need to save them. How do you persist model state during and after training?

**Definition:**
**Checkpointing** is the practice of saving a model's weights, optimizer state, and training metadata to disk at regular intervals during training. Checkpoints enable training resumption, model selection, ensembling, and safe deployment rollbacks.

**Real-life analogy:**
Checkpointing is like saving a video game. You play for two hours, reach a save point, and write your progress to disk. If the power goes out, you restart from the save point, not from the beginning. In AI training, checkpoints are your save points. Some games autosave every 5 minutes; some let you manually save before a boss fight. Training pipelines typically save every epoch (autosave) and after the best validation score (manual save before the boss fight).

**Tiny numeric example:**
A training run with 3 epochs saves checkpoints at each epoch:
- checkpoint_epoch_1.pt: val_acc = 0.72
- checkpoint_epoch_2.pt: val_acc = 0.84
- checkpoint_epoch_3.pt: val_acc = 0.87
For deployment, you would load checkpoint_epoch_3.pt. For an ensemble, you might average the weights of all three checkpoints (this is called "stochastic weight averaging" or "model soup").

**Common confusion:**
- **"Checkpoints are the same as the final model."** Checkpoints contain extra state (optimizer, scheduler, epoch number) that the final model does not need for inference.
- **"You only need the best checkpoint."** Keeping multiple checkpoints lets you run ablation studies, ensemble models, and debug when training went wrong.
- **"Checkpoints are huge."** A full checkpoint (model + optimizer) is ~2x the model size. For a 1B parameter model, that is ~4 GB. Modern training uses sharded checkpoints to distribute this across disks.
- **"Saving every step is safe."** It is safe but I/O-bound. Saving too frequently slows training. A typical compromise is every epoch or every 1000 steps.
- **"You can always resume perfectly."** Resuming requires the exact same code version, library versions, and random seed. Changing any of these can cause divergent results.
- **"Checkpointing is only for crashes."** It is also for preemption in cloud environments (spot instances), for hyperparameter search (pause and resume trials), and for experiment tracking.

**Where it appears in our code:**
`src/phase151/phase151_fine_tuning_pipeline.py` — Saves a checkpoint after every epoch containing model_state_dict, optimizer_state_dict, epoch number, train_loss, val_loss, and val_acc. Also saves a separate final_model.pt with only the weights for inference.
