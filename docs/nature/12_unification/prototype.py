"""
MSPCH-Net: A Multi-Scale Predictive Coding Network
==================================================

This is the prototype described in Part 12 of the nature/ curriculum
(Multi-Scale Predictive Coding Hypothesis, or MSPCH).

The network implements five brain-inspired systems:
  1. Multi-system memory: a fast hippocampus-like associative store
     (one-shot) and a slow cortex-like gradient store (gradual).
  2. Neuromodulation: five neuromodulator signals (DA, ACh, NE, 5-HT, Orexin)
     that gate learning rate, gain, mode, and exploration.
  3. Replay-driven consolidation: an offline replay loop that distills
     episodic memories from fast into slow memory (system consolidation).
  4. Homeostatic scaling: glial-like activity-dependent synaptic
     scaling (Turrigiano 1998), disabled by default in this prototype
     because of interaction with random feature extraction.
  5. Intrinsic motivation: curiosity-driven exploration via
     prediction error as intrinsic reward (Schmidhuber 1991, Pathak 2017).

Task: 2-way 1-shot image classification on a procedurally-generated
synthetic dataset (Gaussian blobs at four distinct positions in an
8x8 image). The 1-shot task cycles through 6 possible pairings.

Expected result: both networks should perform well above the 50%
chance level. MSPCH-Net is meant to *demonstrate* the five systems
working together, not to win an SOTA benchmark. Real performance
will depend on the choice of inner-loop steps, neuromodulator gains,
and the consolidation schedule. See prototype_colab.py for the
PyTorch version with full consolidation and meta-learning.

Run:
    python prototype.py

Outputs:
    plots/mspch_vs_mlp.png   - accuracy curves comparison
    plots/mspch_neuromod.png  - neuromodulator traces
    plots/mspch_curiosity.png - prediction error over time

The code follows the ai-miden AGENTS.md conventions:
  - matplotlib.use('Agg') is set so the script runs headless.
  - Plots are saved to plots/ with descriptive names.
  - Every line explains WHY, not just WHAT.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
# Utilities
# =============================================================================

def one_hot(y, k):
    """Convert integer label y to a one-hot vector of length k."""
    v = np.zeros(k)
    v[y] = 1.0
    return v


def softmax(x, axis=-1):
    """Numerically stable softmax along the given axis."""
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def relu(x):
    return np.maximum(0.0, x)


def relu_grad(x):
    return (x > 0).astype(np.float64)


def kaiming_init(fan_in, fan_out):
    """Kaiming-He initialization for a weight matrix of shape (fan_in, fan_out)."""
    return np.random.randn(fan_in, fan_out) * np.sqrt(2.0 / fan_in)


def make_task(num_classes=2, examples_per_class=1, image_size=8, seed=0,
              num_base_classes=4, noise=0.2):
    """
    Generate a 2-way 1-shot task from a fixed pool of base classes.

    Each base class is a Gaussian blob at a distinct position in an
    8x8 image. The query examples are noisy versions of the support.

    This is deliberately a *small* task so the architecture's
    components can be observed. We are not benchmarking — we are
    demonstrating that all five systems are alive.

    Returns
    -------
    support_x, support_y, query_x, query_y : np.ndarray
    """
    rng = np.random.RandomState(seed)

    # Build a pool of base classes: each is a Gaussian blob at a unique position.
    base_patterns = []
    coords = [(1, 1), (1, 6), (6, 1), (6, 6)]
    for (cy, cx) in coords[:num_base_classes]:
        pattern = np.zeros((image_size, image_size))
        for i in range(image_size):
            for j in range(image_size):
                pattern[i, j] = np.exp(-((i - cy)**2 + (j - cx)**2) / 2.0)
        base_patterns.append(pattern.flatten())

    # Sample num_classes distinct base classes for this task
    chosen = rng.choice(num_base_classes, num_classes, replace=False)

    support_x = []
    support_y = []
    query_x = []
    query_y = []
    for new_label, base_idx in enumerate(chosen):
        for _ in range(examples_per_class):
            support_x.append(base_patterns[base_idx] + 0.02 * rng.randn(image_size*image_size))
            support_y.append(new_label)
        for _ in range(4):
            query_x.append(base_patterns[base_idx] + noise * rng.randn(image_size*image_size))
            query_y.append(new_label)

    return (np.array(support_x), np.array(support_y),
            np.array(query_x), np.array(query_y))


# =============================================================================
# The MSPCH-Net
# =============================================================================

class MSPCHNet:
    """
    A small hierarchical predictive coding network with five brain-inspired
    systems: multi-system memory, neuromodulation, replay, homeostasis,
    and intrinsic motivation.
    """

    def __init__(self, input_dim=64, hidden_dims=(64, 32), output_dim=2,
                 fast_capacity=64, replay_capacity=128, target_activity=0.1,
                 seed=0):
        rng = np.random.RandomState(seed)
        self.rng = rng

        self.layer_sizes = (input_dim,) + tuple(hidden_dims) + (output_dim,)
        # Slow memory: gradient-updated weights AND biases per layer.
        # Biases are stored separately so homeostatic scaling only touches W.
        self.W = []
        self.b = []
        for i in range(len(self.layer_sizes) - 1):
            self.W.append(kaiming_init(self.layer_sizes[i], self.layer_sizes[i+1]))
            self.b.append(np.zeros(self.layer_sizes[i+1]))

        # Fast memory: hippocampus-like key-value associative store.
        # Stored as (key, value) tuples. Retrieval is by cosine similarity.
        self.fast_capacity = fast_capacity
        self.fast_keys = []    # list of (key_vector,)
        self.fast_values = []  # list of (output_one_hot,)

        # Replay buffer for offline consolidation
        self.replay_capacity = replay_capacity
        self.replay_x = []
        self.replay_y = []

        # Neuromodulator levels (initialized to baseline)
        self.da = 0.5    # dopamine: reward prediction error, gates learning
        self.ach = 0.5   # acetylcholine: novelty / attention, gates fast vs slow
        self.ne = 0.5    # norepinephrine: arousal / gain
        self.ser = 0.5   # serotonin: exploration vs exploitation
        self.orex = 0.5  # orexin: behavioral mode (wake / sleep / forage)

        # Homeostatic target: how active each hidden layer should be on average.
        # 5% is roughly what cortex does. The glial-like normalizer will
        # scale weights up or down to enforce this.
        self.target_activity = target_activity
        self.activity_avg = [np.zeros(d) for d in hidden_dims]

        # Step counter (used for sleep / consolidation)
        self.step_count = 0

    # ----- inference -----

    def forward(self, x, return_hidden=False):
        """
        Forward pass through the slow (gradient) memory.
        Returns the output. If return_hidden, also returns hidden activations.
        """
        h = x
        hidden = [h]
        for i in range(len(self.W) - 1):
            h = relu(h @ self.W[i] + self.b[i])
            hidden.append(h)
        out = h @ self.W[-1] + self.b[-1]
        if return_hidden:
            return out, hidden
        return out

    def fast_recall(self, x):
        """
        Recall from the fast (hippocampus-like) memory by cosine similarity.
        Returns the interpolated prediction: how much to trust the fast memory
        depends on ACh (novelty) and on similarity.
        """
        if not self.fast_keys:
            return None, 0.0
        keys = np.array(self.fast_keys)
        sims = (keys @ x) / (np.linalg.norm(keys, axis=1) * np.linalg.norm(x) + 1e-8)
        best = int(np.argmax(sims))
        return self.fast_values[best], float(sims[best])

    def predict(self, x):
        """
        Combined prediction: a soft attention over the fast memory,
        with the slow memory as a learned prior. The fast memory
        stores exact support examples; the slow memory provides a
        generalizing feature extractor.

        The blend weight is high when the fast memory has a confident
        match (high cosine similarity) and ACh is high (novelty/attention).
        """
        slow_out = self.forward(x)
        fast_out, sim = self.fast_recall(x)
        if fast_out is None:
            return slow_out
        # ACh high = trust the fast memory more.
        # Use a sharper softmax-like blend: trust = ACh * sigmoid(scale * sim).
        # scale=10 turns sim=0.5 into ~1.0 and sim=0.0 into ~0.5.
        import math
        if not math.isfinite(sim):
            sim = 0.0
        trust = self.ach / (1.0 + np.exp(-10.0 * (sim - 0.3)))
        return trust * fast_out + (1.0 - trust) * slow_out

    # ----- learning: slow path -----

    def slow_update(self, x, y, learning_rate=0.001):
        """
        Standard backprop on the slow memory.
        Modulated by dopamine (DA) which acts as a learning-rate gate.
        Includes NaN/Inf guards for stability.
        """
        out, hidden = self.forward(x, return_hidden=True)
        p = softmax(out)
        grad = (p - y)
        # Guard: if grad has NaN/Inf, skip this update
        if not np.all(np.isfinite(grad)):
            return
        # The downstream gradient (output layer)
        dW_last = hidden[-1].T @ grad / len(x)
        db_last = np.mean(grad, axis=0)
        self.W[-1] -= learning_rate * self.da * dW_last
        self.b[-1] -= learning_rate * self.da * db_last

        dH = grad @ self.W[-1].T
        for i in range(len(self.W) - 2, -1, -1):
            d_pre = dH * relu_grad(hidden[i+1])
            dW = hidden[i].T @ d_pre / len(x)
            db = np.mean(d_pre, axis=0)
            self.W[i] -= learning_rate * self.da * dW
            self.b[i] -= learning_rate * self.da * db
            dH = d_pre @ self.W[i].T

        # Track running activity for homeostatic scaling (mean across batch)
        for i, h in enumerate(hidden[1:-1]):
            self.activity_avg[i] = 0.95 * self.activity_avg[i] + 0.05 * np.mean(h, axis=0)

        # Clip weights to prevent runaway
        for i in range(len(self.W)):
            self.W[i] = np.clip(self.W[i], -10.0, 10.0)
            self.b[i] = np.clip(self.b[i], -10.0, 10.0)

    # ----- learning: fast path -----

    def fast_store(self, x, y):
        """
        Store (x, y) in the fast memory. Capacity-limited FIFO.
        """
        if len(self.fast_keys) >= self.fast_capacity:
            self.fast_keys.pop(0)
            self.fast_values.pop(0)
        self.fast_keys.append(x.copy())
        self.fast_values.append(y.copy())

    # ----- replay / sleep -----

    def consolidate(self, batch_size=32, learning_rate=0.001):
        """
        Offline replay: sample from the replay buffer and update slow memory.
        This is the 'sleep' step. Runs many gradient steps to consolidate
        recent episodic memories into the slow weights.

        NOTE: Not used in the current prototype. Replaced by
        consolidate_distill to avoid label-ambiguity across tasks.
        """
        if len(self.replay_x) < 2:
            return
        idx = self.rng.choice(len(self.replay_x),
                              min(batch_size, len(self.replay_x)),
                              replace=False)
        x = np.array([self.replay_x[i] for i in idx])
        y = np.array([self.replay_y[i] for i in idx])
        self.slow_update(x, y, learning_rate=learning_rate)

    def consolidate_distill(self, batch_size=16, learning_rate=0.0005):
        """
        Offline distillation: the slow memory learns to predict the
        fast-memory output for replayed examples. This is the
        "compressing episodic memory into semantic knowledge" step.
        Biologically, this corresponds to systems consolidation
        during sleep, where hippocampal replays drive neocortical
        learning (see Part 3 of the curriculum).
        """
        if len(self.replay_x) < 2:
            return
        idx = self.rng.choice(len(self.replay_x),
                              min(batch_size, len(self.replay_x)),
                              replace=False)
        # Build a target by running the fast memory on each replay example.
        targets = []
        for i in idx:
            x = self.replay_x[i]
            fast_out, sim = self.fast_recall(x)
            if fast_out is not None and sim > 0.3:
                targets.append(fast_out)
            else:
                # If no good fast match, skip
                targets.append(None)
        valid = [(i, t) for i, t in zip(idx, targets) if t is not None]
        if not valid:
            return
        x = np.array([self.replay_x[i] for i, _ in valid])
        y = np.array([t for _, t in valid])
        self.slow_update(x, y, learning_rate=learning_rate)

    # ----- homeostatic regulation -----

    def homeostatic_scale(self):
        """
        Glial-like synaptic scaling (Turrigiano 1998).
        If average activity in a hidden layer drifts from target, scale
        the incoming weights up or down multiplicatively. Slow update.
        Conservative by design: small step, hard cap.
        """
        for i in range(len(self.W) - 1):
            if not np.all(np.isfinite(self.activity_avg[i])):
                continue
            avg = float(np.mean(self.activity_avg[i]))
            # ratio: how far are we from target
            ratio = self.target_activity / (avg + 1e-6)
            # 0.5% update per step, slow like a glial time scale
            scale = 0.995 + 0.005 * ratio
            # hard cap to avoid runaway
            scale = float(np.clip(scale, 0.95, 1.05))
            self.W[i] *= scale

        # Safety: clip any NaN/Inf that may have crept in
        for i in range(len(self.W)):
            self.W[i] = np.nan_to_num(self.W[i], nan=0.0, posinf=1.0, neginf=-1.0)
            self.b[i] = np.nan_to_num(self.b[i], nan=0.0, posinf=1.0, neginf=-1.0)

    # ----- neuromodulator update -----

    def update_neuromodulators(self, reward, prediction_error, novelty):
        """
        Update the five neuromodulator levels based on reward, error, novelty.
        This is the *fast* neuromodulation (seconds scale).
        """
        # Dopamine = reward prediction error (smoothed update)
        self.da = float(np.clip(self.da + 0.1 * (reward - self.da), 0.0, 1.0))
        # ACh = novelty (high when something is new)
        self.ach = float(np.clip(0.3 + 0.7 * novelty, 0.0, 1.0))
        # NE = arousal (driven by uncertainty / surprise)
        self.ne = float(np.clip(0.3 + 0.7 * prediction_error, 0.0, 1.0))
        # 5-HT = exploitation vs exploration (drops when reward is high)
        self.ser = float(np.clip(0.5 + 0.5 * (1.0 - reward), 0.0, 1.0))
        # Orexin = mode switch (high during active learning, low during sleep)
        self.orex = float(np.clip(0.5 + 0.5 * (1.0 - 0.5 * (self.step_count % 50 < 10)), 0.0, 1.0))

    # ----- one-shot training step -----

    def train_step(self, x_support, y_support, x_query, y_query,
                   inner_lr=0.005, outer_lr=0.001, sleep_every=10, n_sleep=5):
        """
        One outer step of few-shot training.

        1. Use the support set to do *fast* adaptation:
           - Store the support in fast memory.
           - For each support example, do one or two inner-loop gradient
             steps on the slow weights (meta-learning style).
        2. Predict on the query set using the combined predictor.
        3. Compute loss and prediction error.
        4. Update neuromodulators based on accuracy.
        5. If it's time, do offline consolidation (sleep).
        6. Update homeostatic scaling.

        Returns: (loss, accuracy, prediction_error, intrinsic_reward)
        """
        self.step_count += 1

        # 1. Fast adaptation on the support set.
        # The fast memory carries the inner-loop adaptation load.
        # The slow memory is only updated during consolidation (sleep).
        # This is biologically faithful: cortex is too stable to update
        # in one shot, hippocampus handles the one-shot binding.
        for x_s, y_s in zip(x_support, y_support):
            # Store in fast memory (one-shot)
            self.fast_store(x_s, y_s)
            # And in the replay buffer for future consolidation
            if len(self.replay_x) >= self.replay_capacity:
                self.replay_x.pop(0)
                self.replay_y.pop(0)
            self.replay_x.append(x_s.copy())
            self.replay_y.append(y_s.copy())

        # 2. Predict on query
        preds = np.array([self.predict(xq) for xq in x_query])
        p = softmax(preds, axis=1)
        correct = (np.argmax(p, axis=1) == y_query).astype(np.float64)
        accuracy = float(np.mean(correct))

        # 3. Loss and prediction error
        y_onehot = np.array([one_hot(int(y), self.layer_sizes[-1]) for y in y_query])
        loss = -np.mean(np.sum(y_onehot * np.log(p + 1e-8), axis=1))
        prediction_error = float(np.mean(np.abs(p - y_onehot)))

        # 4. Intrinsic reward: novelty = how wrong we were
        # (Schmidhuber 1991, Pathak 2017)
        intrinsic_reward = prediction_error
        # Plus an extrinsic reward signal from accuracy
        extrinsic_reward = accuracy
        # Total reward
        reward = 0.5 * extrinsic_reward + 0.5 * intrinsic_reward

        # 5. Neuromodulator update
        novelty = prediction_error
        self.update_neuromodulators(reward, prediction_error, novelty)

        # 6. Sleep / consolidation.
        # The slow memory learns by *distillation* from the fast memory:
        # it tries to predict the fast-memory output (the one-shot binding).
        # This is biologically faithful: during sleep, hippocampus replays
        # recent episodes and the neocortex learns to extract the gist
        # (system consolidation, see Part 3 of the curriculum).
        if self.step_count % sleep_every == 0 and len(self.replay_x) >= 2:
            for _ in range(n_sleep):
                self.consolidate_distill(learning_rate=outer_lr)

        # 7. Homeostatic scaling (glial).
        # Disabled in this prototype because it interacts poorly with
        # the random feature extractor when there's no supervised loss
        # to anchor the activities. A full implementation would only
        # scale when the network is actively training on labeled data.
        # self.homeostatic_scale()

        return loss, accuracy, prediction_error, intrinsic_reward


# =============================================================================
# Baseline: an equivalent MLP (no brain-inspired systems)
# =============================================================================

class BaselineMLP:
    """An equivalent two-layer MLP, trained with standard backprop."""

    def __init__(self, input_dim=64, hidden_dim=32, output_dim=2, lr=0.01, seed=0):
        rng = np.random.RandomState(seed)
        self.W1 = kaiming_init(input_dim, hidden_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = kaiming_init(hidden_dim, output_dim)
        self.b2 = np.zeros(output_dim)
        self.lr = lr

    def forward(self, x):
        h = relu(x @ self.W1 + self.b1)
        out = h @ self.W2 + self.b2
        return out, h

    def train_step(self, x, y):
        out, h = self.forward(x)
        p = softmax(out)
        grad_out = (p - y) / len(x)
        dW2 = h.T @ grad_out
        db2 = np.mean(grad_out, axis=0)
        grad_h = grad_out @ self.W2.T * relu_grad(h)
        dW1 = x.T @ grad_h
        db1 = np.mean(grad_h, axis=0)
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

    def predict(self, x):
        out, _ = self.forward(x)
        return out


# =============================================================================
# The experiment
# =============================================================================

def run_experiment(num_outer_steps=200, seed=42, window=20):
    """
    Run a 5-way 1-shot learning experiment comparing MSPCH-Net to a baseline MLP.

    The networks are presented with the same sequence of few-shot tasks
    drawn from a fixed pool of base classes. We plot rolling-mean
    accuracy vs outer step. The hypothesis: MSPCH-Net's fast memory +
    replay consolidation lets it converge faster than a baseline trained
    with standard backprop.

    Returns: dict with results for both networks.
    """
    print("=" * 60)
    print("MSPCH-Net vs Baseline MLP: 2-way 1-shot learning")
    print("=" * 60)

    # Initialize networks
    mspch = MSPCHNet(seed=seed)
    baseline = BaselineMLP(seed=seed, lr=0.01)

    output_dim = 2
    acc_mspch = []
    acc_baseline = []
    loss_mspch = []
    pe_mspch = []
    da_trace = []
    ach_trace = []
    ne_trace = []

    for step in range(num_outer_steps):
        # Sample a new task from the fixed base-class pool.
        # Cycle through the 6 possible 2-way subsets of the 4 base classes.
        task_idx = step % 6
        task_seed = task_idx * 137
        support_x, support_y, query_x, query_y = make_task(
            seed=task_seed, noise=0.2
        )
        y_support_onehot = np.array([one_hot(int(y), output_dim) for y in support_y])

        # ---- MSPCH-Net ----
        loss_m, acc_m, pe_m, ir_m = mspch.train_step(
            support_x, y_support_onehot, query_x, query_y,
            inner_lr=0.01, outer_lr=0.001, sleep_every=5, n_sleep=2
        )
        acc_mspch.append(acc_m)
        loss_mspch.append(loss_m)
        pe_mspch.append(pe_m)
        da_trace.append(mspch.da)
        ach_trace.append(mspch.ach)
        ne_trace.append(mspch.ne)

        # ---- Baseline MLP ----
        # The baseline trains on the support set. We give it only
        # one inner-loop step — equivalent to a single gradient step
        # on the 2-example support set. This is the *fair* 1-shot
        # comparison: the baseline gets to update its weights from
        # the support set, but only once.
        baseline.train_step(support_x, y_support_onehot)
        preds = np.array([baseline.predict(xq) for xq in query_x])
        p = softmax(preds, axis=1)
        acc_b = float(np.mean(np.argmax(p, axis=1) == query_y))
        acc_baseline.append(acc_b)

        if (step + 1) % 25 == 0 or step == 0:
            # Rolling mean of last `window` steps
            def roll(x):
                if len(x) < window:
                    return float(np.mean(x))
                return float(np.mean(x[-window:]))
            print(f"Step {step+1:4d} | "
                  f"MSPCH acc={roll(acc_mspch):.3f} (raw {acc_m:.2f}) "
                  f"loss={loss_m:.3f} pe={pe_m:.3f} | "
                  f"Baseline acc={roll(acc_baseline):.3f} (raw {acc_b:.2f}) | "
                  f"DA={mspch.da:.2f} ACh={mspch.ach:.2f} NE={mspch.ne:.2f}")

    # Compute rolling-mean final accuracies
    def roll(x, w):
        if len(x) < w:
            return float(np.mean(x))
        return float(np.mean(x[-w:]))

    mspch_final = roll(acc_mspch, window)
    baseline_final = roll(acc_baseline, window)
    print()
    print(f"Final rolling-mean accuracy (last {window} steps):")
    print(f"  MSPCH-Net:  {mspch_final:.3f}")
    print(f"  Baseline:   {baseline_final:.3f}")

    # Save plots
    os.makedirs("plots", exist_ok=True)

    # Accuracy curves (with rolling mean overlay)
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(acc_mspch, alpha=0.3, color="#1f77b4", label="MSPCH-Net (raw)")
    ax.plot(acc_baseline, alpha=0.3, color="#ff7f0e", label="Baseline (raw)")
    # Rolling means
    mspch_smooth = np.convolve(acc_mspch, np.ones(window)/window, mode="valid")
    baseline_smooth = np.convolve(acc_baseline, np.ones(window)/window, mode="valid")
    ax.plot(range(window-1, len(acc_mspch)), mspch_smooth,
            color="#1f77b4", linewidth=2.5, label=f"MSPCH-Net (rolling-{window})")
    ax.plot(range(window-1, len(acc_baseline)), baseline_smooth,
            color="#ff7f0e", linewidth=2.5, label=f"Baseline (rolling-{window})")
    ax.axhline(1/2, color="gray", linestyle="--", alpha=0.4, label="Chance (50%)")
    ax.set_xlabel("Outer step (number of 2-way 1-shot tasks)")
    ax.set_ylabel("Query-set accuracy")
    ax.set_title("MSPCH-Net vs Baseline MLP: 2-way 1-shot learning")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig("plots/mspch_vs_mlp.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/mspch_vs_mlp.png")

    # Neuromodulator traces
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(da_trace, label="Dopamine (DA)", linewidth=2)
    ax.plot(ach_trace, label="Acetylcholine (ACh)", linewidth=2)
    ax.plot(ne_trace, label="Norepinephrine (NE)", linewidth=2)
    ax.set_xlabel("Outer step")
    ax.set_ylabel("Neuromodulator level")
    ax.set_title("Neuromodulator dynamics during learning")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/mspch_neuromod.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/mspch_neuromod.png")

    # Curiosity signal
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(pe_mspch, color="#2ca02c", linewidth=2)
    ax.set_xlabel("Outer step")
    ax.set_ylabel("Mean prediction error (curiosity signal)")
    ax.set_title("Curiosity signal: prediction error over time")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/mspch_curiosity.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/mspch_curiosity.png")

    return {
        "mspch": {"acc": acc_mspch, "loss": loss_mspch},
        "baseline": {"acc": acc_baseline},
        "mspch_final_rolling": mspch_final,
        "baseline_final_rolling": baseline_final,
    }


if __name__ == "__main__":
    run_experiment()
