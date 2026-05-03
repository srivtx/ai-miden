#!/usr/bin/env python3
"""
Phase 130: Production Monitoring and MLOps — NumPy Concept Demo
================================================================
This script simulates production LLM monitoring and MLOps to demonstrate:

  1. Production traffic simulation with latency distributions
  2. Error rate tracking over time
  3. Drift detection: sudden change in query distribution (KL divergence)
  4. A/B testing: comparing two model versions on simulated metrics
  5. Alert thresholds and dashboard visualization

Key insight: monitoring is not about collecting data; it is about
building signals that fire before users complain. Drift detection,
latency percentiles, and A/B tests are the early warning system.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(130)

# =============================================================================
# SECTION 1: SIMULATE PRODUCTION TRAFFIC
# =============================================================================
# We generate 200 synthetic requests. The first 100 are "benign" (short,
# simple queries). The last 100 are "complex" (longer, more technical).
# This simulates a real-world event: a product launch, a viral tweet,
# or a UI change that causes users to paste longer documents.

N_REQUESTS = 200
DRIFT_START = 100  # drift starts at request 100

# Benign requests: short prompts, fast generation
benign_input_lens = np.random.normal(loc=45, scale=12, size=DRIFT_START).astype(int)
benign_input_lens = np.clip(benign_input_lens, 10, 120)
benign_output_lens = np.random.normal(loc=65, scale=18, size=DRIFT_START).astype(int)
benign_output_lens = np.clip(benign_output_lens, 15, 150)

# Complex requests: longer prompts, slower generation
complex_input_lens = np.random.normal(loc=180, scale=40, size=N_REQUESTS - DRIFT_START).astype(int)
complex_input_lens = np.clip(complex_input_lens, 80, 400)
complex_output_lens = np.random.normal(loc=220, scale=55, size=N_REQUESTS - DRIFT_START).astype(int)
complex_output_lens = np.clip(complex_output_lens, 60, 450)

input_lengths = np.concatenate([benign_input_lens, complex_input_lens])
output_lengths = np.concatenate([benign_output_lens, complex_output_lens])

print("="*70)
print("Phase 130: Production Monitoring and MLOps — NumPy Concept Demo")
print("="*70)
print(f"Total requests: {N_REQUESTS}")
print(f"Drift injection at request: {DRIFT_START}")
print(f"Benign input length:  mean={benign_input_lens.mean():.0f}, std={benign_input_lens.std():.0f}")
print(f"Complex input length: mean={complex_input_lens.mean():.0f}, std={complex_input_lens.std():.0f}")

# =============================================================================
# SECTION 2: SIMULATE LATENCY AND ERRORS
# =============================================================================
# Latency is a function of input length, output length, and random noise.
# We model TTFT as input-bound and total latency as output-bound.
# Errors increase under load and with longer outputs.

def simulate_latency_and_errors(input_lens, output_lens, base_ttf=0.002, base_gen=0.015):
    """
    Simulate latency and errors for each request.
    WHY base_ttf=2ms/token? Prompt processing is fast but scales linearly.
    WHY base_gen=15ms/token? Generation is memory-bound and slower.
    WHY error probability rises with output length? Longer generations
    have more opportunities for timeout, repetition, or context overflow.
    """
    ttfts = input_lens * base_ttf + np.random.exponential(0.01, size=len(input_lens))
    tpots = base_gen + np.random.exponential(0.005, size=len(input_lens))
    total_latencies = ttfts + output_lens * tpots

    # Error probability: base 1% + 0.5% per 100 output tokens + noise
    error_probs = 0.01 + 0.005 * (output_lens / 100) + np.random.normal(0, 0.005, size=len(input_lens))
    error_probs = np.clip(error_probs, 0, 0.5)
    errors = np.random.rand(len(input_lens)) < error_probs

    return ttfts, tpots, total_latencies, errors

ttfts, tpots, latencies, errors = simulate_latency_and_errors(input_lengths, output_lengths)

print(f"\n--- Latency Statistics ---")
print(f"Mean latency:     {latencies.mean():.3f} s")
print(f"p50 latency:      {np.percentile(latencies, 50):.3f} s")
print(f"p95 latency:      {np.percentile(latencies, 95):.3f} s")
print(f"p99 latency:      {np.percentile(latencies, 99):.3f} s")
print(f"Error rate:       {errors.mean()*100:.1f}%")

# =============================================================================
# SECTION 3: DRIFT DETECTION
# =============================================================================
# We use a sliding window to detect drift. At each step, we compare the
# distribution of the last 20 requests against the baseline (first 50).
# We use KL divergence on binned input lengths and z-score on latency.

def compute_drift_scores(input_lens, latencies, window_size=20, baseline_size=50):
    """
    Compute drift score at each time step using sliding windows.
    WHY KS statistic instead of KL? KS is non-parametric, does not require
    binning, and is robust with small sample sizes. KL divergence with
    histograms is unstable when bins are empty.
    """
    drift_scores = []
    for t in range(baseline_size, len(input_lens)):
        # Baseline distribution (fixed: first baseline_size requests)
        baseline = input_lens[:baseline_size]
        # Current window (last window_size requests ending at t)
        current = input_lens[max(0, t - window_size):t]

        # KS statistic on input lengths
        # WHY max? KS is symmetric but we take max distance for a single scalar
        ks_stat = np.max(np.abs(
            np.sort(baseline)[:, None] - np.sort(current)[None, :]
        ))
        # Simplified: use empirical CDF max distance
        # Actually compute proper KS statistic manually for clarity
        def _ecdf(x):
            x_sorted = np.sort(x)
            y = np.arange(1, len(x_sorted) + 1) / len(x_sorted)
            return x_sorted, y

        x_base, y_base = _ecdf(baseline)
        x_curr, y_curr = _ecdf(current)
        x_all = np.sort(np.unique(np.concatenate([x_base, x_curr])))
        y_base_interp = np.searchsorted(x_base, x_all, side='right') / len(x_base)
        y_curr_interp = np.searchsorted(x_curr, x_all, side='right') / len(x_curr)
        ks = np.max(np.abs(y_base_interp - y_curr_interp))

        # Latency z-score: compare current window latency to baseline
        baseline_lat_mean = latencies[:baseline_size].mean()
        baseline_lat_std = latencies[:baseline_size].std() + 1e-6
        current_lat = latencies[max(0, t - window_size):t]
        current_lat_mean = current_lat.mean() if len(current_lat) > 0 else baseline_lat_mean
        z_score = (current_lat_mean - baseline_lat_mean) / baseline_lat_std

        # Combined drift score: KS dominates early, latency confirms
        combined = ks + max(0, z_score - 2) * 0.3
        drift_scores.append(combined)

    return np.array(drift_scores)

drift_scores = compute_drift_scores(input_lengths, latencies)
drift_threshold = 0.8
alerts = drift_scores > drift_threshold
alert_indices = np.where(alerts)[0] + 50  # offset by baseline_size

print(f"\n--- Drift Detection ---")
print(f"Drift threshold: {drift_threshold}")
print(f"Alerts fired: {alerts.sum()} times")
if len(alert_indices) > 0:
    print(f"First alert at request: {alert_indices[0]}")
    print(f"Last alert at request:  {alert_indices[-1]}")

# =============================================================================
# SECTION 4: A/B TEST SIMULATION
# =============================================================================
# We simulate two model versions: A (baseline) and B (new).
# Version B has slightly higher latency but better output quality.
# We route 50% of traffic to each and compare metrics.

N_AB_REQUESTS = 200

# Version A: baseline
a_input_lens = np.random.normal(loc=60, scale=15, size=N_AB_REQUESTS).astype(int)
a_input_lens = np.clip(a_input_lens, 15, 150)
a_output_lens = np.random.normal(loc=70, scale=20, size=N_AB_REQUESTS).astype(int)
a_output_lens = np.clip(a_output_lens, 20, 160)
a_latencies = a_input_lens * 0.002 + a_output_lens * 0.018 + np.random.exponential(0.02, N_AB_REQUESTS)
a_satisfaction = np.random.beta(7, 3, N_AB_REQUESTS) * 5  # mean ~3.5

# Version B: new model (slightly slower, better quality)
b_input_lens = np.random.normal(loc=60, scale=15, size=N_AB_REQUESTS).astype(int)
b_input_lens = np.clip(b_input_lens, 15, 150)
b_output_lens = np.random.normal(loc=75, scale=18, size=N_AB_REQUESTS).astype(int)
b_output_lens = np.clip(b_output_lens, 20, 170)
b_latencies = b_input_lens * 0.002 + b_output_lens * 0.020 + np.random.exponential(0.025, N_AB_REQUESTS)
b_satisfaction = np.random.beta(8, 2, N_AB_REQUESTS) * 5  # mean ~4.0

print(f"\n--- A/B Test Simulation ---")
print(f"Version A (baseline):")
print(f"  Mean latency:      {a_latencies.mean():.3f} s")
print(f"  Mean output len:   {a_output_lens.mean():.0f} tokens")
print(f"  Mean satisfaction: {a_satisfaction.mean():.2f}/5.0")
print(f"Version B (new):")
print(f"  Mean latency:      {b_latencies.mean():.3f} s")
print(f"  Mean output len:   {b_output_lens.mean():.0f} tokens")
print(f"  Mean satisfaction: {b_satisfaction.mean():.2f}/5.0")

# Statistical significance (t-test approximation)
pooled_std = np.sqrt((a_latencies.var() + b_latencies.var()) / 2)
t_stat = (b_latencies.mean() - a_latencies.mean()) / (pooled_std / np.sqrt(N_AB_REQUESTS))
print(f"Latency t-statistic: {t_stat:.2f} (|t|>2 is significant)")

# =============================================================================
# SECTION 5: COST TRACKING
# =============================================================================
# We assign a mock cost per token and compute total spend.

cost_per_input_token = 0.00001
cost_per_output_token = 0.00003

total_cost = (input_lengths.sum() * cost_per_input_token +
              output_lengths.sum() * cost_per_output_token)
cost_benign = (benign_input_lens.sum() * cost_per_input_token +
               benign_output_lens.sum() * cost_per_output_token)
cost_complex = (complex_input_lens.sum() * cost_per_input_token +
                complex_output_lens.sum() * cost_per_output_token)

print(f"\n--- Cost Tracking ---")
print(f"Total cost (all requests):     ${total_cost:.2f}")
print(f"Cost per benign request:       ${cost_benign/DRIFT_START:.4f}")
print(f"Cost per complex request:      ${cost_complex/(N_REQUESTS-DRIFT_START):.4f}")
print(f"Complex/benign cost ratio:     {(cost_complex/(N_REQUESTS-DRIFT_START))/(cost_benign/DRIFT_START):.1f}x")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Plot 1: Latency over time with drift line
ax = axes[0, 0]
ax.plot(latencies, '-', color='#3498db', alpha=0.7, linewidth=1)
ax.axvline(DRIFT_START, color='#e74c3c', linestyle='--', linewidth=2, label='Drift injection')
ax.axhline(np.percentile(latencies, 95), color='#e67e22', linestyle=':', linewidth=1.5, label='p95 baseline')
ax.set_xlabel('Request Index')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Request Latency Over Time')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Error rate over time (rolling window)
ax = axes[0, 1]
window = 20
rolling_error = np.convolve(errors, np.ones(window)/window, mode='valid')
ax.plot(range(window-1, len(errors)), rolling_error*100, '-', color='#e74c3c', linewidth=2)
ax.axvline(DRIFT_START, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.5)
ax.set_xlabel('Request Index')
ax.set_ylabel('Error Rate (%)')
ax.set_title(f'Rolling Error Rate ({window}-request window)')
ax.grid(True, alpha=0.3)

# Plot 3: Drift score over time
ax = axes[0, 2]
ax.plot(range(50, 50+len(drift_scores)), drift_scores, '-', color='#9b59b6', linewidth=2)
ax.axhline(drift_threshold, color='#e74c3c', linestyle='--', linewidth=2, label=f'Alert threshold={drift_threshold}')
ax.axvline(DRIFT_START, color='gray', linestyle=':', linewidth=1.5, label='Drift injection')
ax.fill_between(range(50, 50+len(drift_scores)), drift_scores, drift_threshold,
                where=(drift_scores > drift_threshold), color='#e74c3c', alpha=0.3)
ax.set_xlabel('Request Index')
ax.set_ylabel('Drift Score')
ax.set_title('Drift Score Over Time')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Input length distribution (before vs after drift)
ax = axes[1, 0]
ax.hist(benign_input_lens, bins=20, alpha=0.6, color='#3498db', label='Benign (requests 0-99)', edgecolor='black')
ax.hist(complex_input_lens, bins=20, alpha=0.6, color='#e74c3c', label='Complex (requests 100-199)', edgecolor='black')
ax.set_xlabel('Input Length (tokens)')
ax.set_ylabel('Count')
ax.set_title('Input Length Distribution')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 5: A/B test comparison
ax = axes[1, 1]
x = np.arange(3)
width = 0.35
metrics_a = [a_latencies.mean(), a_output_lens.mean(), a_satisfaction.mean()]
metrics_b = [b_latencies.mean(), b_output_lens.mean(), b_satisfaction.mean()]
# Normalize for visualization
norm_a = [metrics_a[0], metrics_a[1]/10, metrics_a[2]]
norm_b = [metrics_b[0], metrics_b[1]/10, metrics_b[2]]
ax.bar(x - width/2, norm_a, width, label='Version A (baseline)', color='#3498db', edgecolor='black')
ax.bar(x + width/2, norm_b, width, label='Version B (new)', color='#27ae60', edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels(['Latency (s)', 'Output len (/10)', 'Satisfaction'])
ax.set_ylabel('Normalized Score')
ax.set_title('A/B Test: Version A vs. B')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 6: Token usage over time
ax = axes[1, 2]
total_tokens = input_lengths + output_lengths
ax.plot(total_tokens, '-', color='#27ae60', alpha=0.7, linewidth=1)
ax.axvline(DRIFT_START, color='#e74c3c', linestyle='--', linewidth=2, label='Drift injection')
rolling_tokens = np.convolve(total_tokens, np.ones(window)/window, mode='valid')
ax.plot(range(window-1, len(total_tokens)), rolling_tokens, '-', color='#145a32', linewidth=2, label=f'{window}-req avg')
ax.set_xlabel('Request Index')
ax.set_ylabel('Total Tokens')
ax.set_title('Token Usage Over Time')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase130', exist_ok=True)
plt.savefig('src/phase130/monitoring_concepts.png', dpi=150)
print("\nSaved plot to src/phase130/monitoring_concepts.png")

# =============================================================================
# SECTION 7: ALERT LOG
# =============================================================================

print("\n" + "="*70)
print("ALERT LOG")
print("="*70)
if len(alert_indices) > 0:
    print(f"ALERT: Drift detected at request {alert_indices[0]} (score={drift_scores[alert_indices[0]-50]:.2f})")
    print(f"  Trigger: Input length KS statistic + latency z-score exceeded threshold")
    print(f"  Recommended action: Investigate traffic source; check for UI bug or abuse")
    for idx in alert_indices[1:5]:
        print(f"ALERT: Drift continues at request {idx} (score={drift_scores[idx-50]:.2f})")
    if len(alert_indices) > 5:
        print(f"... and {len(alert_indices)-5} additional alerts")
else:
    print("No alerts fired.")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Simulated {N_REQUESTS} requests with drift at request {DRIFT_START}")
print(f"Latency: p50={np.percentile(latencies,50):.2f}s, p95={np.percentile(latencies,95):.2f}s, p99={np.percentile(latencies,99):.2f}s")
print(f"Error rate: {errors.mean()*100:.1f}%")
print(f"Drift alerts: {alerts.sum()} (first at request {alert_indices[0] if len(alert_indices)>0 else 'N/A'})")
print(f"A/B test: Version B satisfaction {b_satisfaction.mean():.2f} vs. A {a_satisfaction.mean():.2f}")
print(f"Cost: ${total_cost:.2f} total; complex requests cost {(cost_complex/(N_REQUESTS-DRIFT_START))/(cost_benign/DRIFT_START):.1f}x more")
print(f"\nKey lessons:")
print("  1. Monitor p95/p99 latency, not just mean.")
print("  2. Drift detection needs multiple orthogonal signals (input, output, latency).")
print("  3. Sliding windows catch drift faster than global comparisons.")
print("  4. A/B tests validate new models on real traffic before full rollout.")
print("  5. Cost tracking per request reveals which users drive spend.")
print("  6. Rolling error rates smooth noise and reveal trends.")
print("  7. Alerts without runbooks are just noise; pair detection with action.")
print("="*70)
