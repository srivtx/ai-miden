#!/usr/bin/env python3
"""
Phase 58: Time Series Forecasting — NumPy Concept Demo
=======================================================
This script demonstrates how to predict future values from past
observations, handling trends, seasonality, and autocorrelation.

Key insight: The future depends on the past, but not all past
values are equally important. Recent history matters more.

Concepts demonstrated:
  - Time series properties (trend, seasonality, autocorrelation)
  - Autoregressive (AR) model
  - Exponential smoothing
  - Seasonality decomposition
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(58)

# =============================================================================
# SECTION 1: GENERATE SYNTHETIC TIME SERIES
# =============================================================================
# Components: trend + seasonality + noise

n_points = 120
time = np.arange(n_points)

# Trend: linear upward
trend = 0.05 * time

# Seasonality: sine wave with period 24 (e.g., daily cycle)
seasonality = 2.0 * np.sin(2 * np.pi * time / 24)

# Noise: random fluctuations
noise = np.random.normal(0, 0.5, n_points)

# Combined series
series = trend + seasonality + noise + 10  # base level = 10

print("="*60)
print("Phase 58: Time Series Forecasting")
print("="*60)
print(f"\nGenerated series: {n_points} points")
print(f"Components: trend (slope=0.05) + seasonality (period=24) + noise (σ=0.5)")

# Train/test split (last 20 points for testing)
train = series[:-20]
test = series[-20:]
train_time = time[:-20]
test_time = time[-20:]

print(f"Train: {len(train)} points, Test: {len(test)} points")

# =============================================================================
# SECTION 2: AUTOCORRELATION
# =============================================================================

def autocorr(x, lag):
    """Compute autocorrelation at given lag."""
    x = x - np.mean(x)
    c0 = np.sum(x ** 2)
    c_lag = np.sum(x[:-lag] * x[lag:])
    return c_lag / c0

lags = range(1, 25)
acf_values = [autocorr(train, lag) for lag in lags]

print(f"\n--- Autocorrelation ---")
print(f"Lag-1 autocorrelation: {acf_values[0]:.3f}")
print(f"Peak at lag-24: {acf_values[23]:.3f} (matches seasonality period)")

# =============================================================================
# SECTION 3: MOVING AVERAGE FORECAST
# =============================================================================

window = 12
ma_forecast = []
for i in range(len(test)):
    if i == 0:
        # First forecast: average of last 'window' training points
        ma = np.mean(train[-window:])
    else:
        # Subsequent: average of last 'window' points (including prior forecasts)
        available = np.concatenate([train, ma_forecast])
        ma = np.mean(available[-window:])
    ma_forecast.append(ma)

ma_forecast = np.array(ma_forecast)
ma_mae = np.mean(np.abs(ma_forecast - test))
print(f"\n--- Moving Average (window={window}) ---")
print(f"MAE: {ma_mae:.3f}")

# =============================================================================
# SECTION 4: EXPONENTIAL SMOOTHING
# =============================================================================

def exp_smooth(series, alpha):
    """Simple exponential smoothing."""
    smoothed = np.zeros(len(series))
    smoothed[0] = series[0]
    for t in range(1, len(series)):
        smoothed[t] = alpha * series[t] + (1 - alpha) * smoothed[t-1]
    return smoothed

# Find best alpha on training data
best_alpha = None
best_mae = float('inf')
for alpha in [0.1, 0.3, 0.5, 0.7, 0.9]:
    smoothed = exp_smooth(train, alpha)
    # One-step-ahead forecast error
    forecast = np.concatenate([[train[0]], smoothed[:-1]])
    mae = np.mean(np.abs(forecast[1:] - train[1:]))
    if mae < best_mae:
        best_mae = mae
        best_alpha = alpha

print(f"\n--- Exponential Smoothing ---")
print(f"Best alpha: {best_alpha} (validation MAE: {best_mae:.3f})")

# Forecast with best alpha
smoothed_train = exp_smooth(train, best_alpha)
es_forecast = []
last_smoothed = smoothed_train[-1]
for i in range(len(test)):
    es_forecast.append(last_smoothed)
    # Update smoothed value with actual test value (for next step)
    if i < len(test) - 1:
        last_smoothed = best_alpha * test[i] + (1 - best_alpha) * last_smoothed

es_forecast = np.array(es_forecast)
es_mae = np.mean(np.abs(es_forecast - test))
print(f"Test MAE: {es_mae:.3f}")

# =============================================================================
# SECTION 5: AUTOREGRESSIVE MODEL (AR(3))
# =============================================================================

print(f"\n--- Autoregressive Model (AR(3)) ---")

# Build design matrix: [x_{t-1}, x_{t-2}, x_{t-3}] -> x_t
p = 3
X_ar = np.zeros((len(train) - p, p))
y_ar = train[p:]
for i in range(p):
    X_ar[:, i] = train[p-1-i:-1-i]

# Add bias
X_ar = np.column_stack([np.ones(len(X_ar)), X_ar])

# Least squares solution
w_ar = np.linalg.lstsq(X_ar, y_ar, rcond=None)[0]
c, phi1, phi2, phi3 = w_ar
print(f"AR coefficients: c={c:.3f}, φ1={phi1:.3f}, φ2={phi2:.3f}, φ3={phi3:.3f}")

# Forecast
ar_forecast = []
history = list(train[-p:])
for i in range(len(test)):
    pred = c + phi1*history[-1] + phi2*history[-2] + phi3*history[-3]
    ar_forecast.append(pred)
    history.append(test[i] if i == 0 else ar_forecast[-1])

ar_forecast = np.array(ar_forecast)
ar_mae = np.mean(np.abs(ar_forecast - test))
print(f"Test MAE: {ar_mae:.3f}")

# =============================================================================
# SECTION 6: SEASONALITY DECOMPOSITION
# =============================================================================

print(f"\n--- Seasonality Decomposition ---")

# Estimate trend with 24-point moving average (2x the seasonality period)
trend_est = np.convolve(series, np.ones(24)/24, mode='same')

# Detrended series
detrended = series - trend_est

# Estimate seasonality: average detrended value for each position in the cycle
period = 24
seasonal_est = np.zeros(period)
counts = np.zeros(period)
for i in range(len(detrended)):
    idx = i % period
    seasonal_est[idx] += detrended[i]
    counts[idx] += 1
seasonal_est /= counts

# Replicate seasonality to full length
full_seasonal = np.tile(seasonal_est, len(series) // period + 1)[:len(series)]

# Residual
residual = series - trend_est - full_seasonal

print(f"Trend range: [{trend_est.min():.2f}, {trend_est.max():.2f}]")
print(f"Seasonal amplitude: {seasonal_est.max() - seasonal_est.min():.2f}")
print(f"Residual std: {residual.std():.3f}")

# Verify: recompose
reconstructed = trend_est + full_seasonal + residual
reconstruction_error = np.mean(np.abs(reconstructed - series))
print(f"Reconstruction error: {reconstruction_error:.6f} (should be ~0)")

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Full series with components
ax = axes[0, 0]
ax.plot(time, series, 'b-', alpha=0.7, label='Original', linewidth=1.5)
ax.plot(time, trend_est, 'r--', label='Trend', linewidth=2)
ax.plot(time, full_seasonal + 10, 'g-', alpha=0.5, label='Seasonality (shifted)', linewidth=1.5)
ax.axvline(x=train_time[-1], color='gray', linestyle=':', alpha=0.5, label='Train/Test split')
ax.set_title('Time Series with Trend and Seasonality')
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Autocorrelation
ax = axes[0, 1]
ax.bar(lags, acf_values, color='#3498db', edgecolor='black', alpha=0.7)
ax.axhline(y=0, color='black', linewidth=0.5)
ax.axhline(y=0.2, color='red', linestyle='--', alpha=0.5, label='Significance threshold')
ax.axhline(y=-0.2, color='red', linestyle='--', alpha=0.5)
ax.axvline(x=24, color='green', linestyle='--', alpha=0.5, label='Seasonality period (24)')
ax.set_title('Autocorrelation Function')
ax.set_xlabel('Lag')
ax.set_ylabel('Autocorrelation')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Forecast comparison
ax = axes[1, 0]
ax.plot(train_time, train, 'b-', alpha=0.5, label='Train', linewidth=1.5)
ax.plot(test_time, test, 'b-', label='Actual', linewidth=2)
ax.plot(test_time, ma_forecast, 'r--', label=f'Moving Avg (MAE={ma_mae:.2f})', linewidth=2)
ax.plot(test_time, es_forecast, 'g-.', label=f'Exp Smooth (MAE={es_mae:.2f})', linewidth=2)
ax.plot(test_time, ar_forecast, 'm:', label=f'AR(3) (MAE={ar_mae:.2f})', linewidth=2)
ax.set_title('Forecast Comparison')
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Decomposition
ax = axes[1, 1]
ax.plot(time, series, 'b-', alpha=0.5, label='Original')
ax.plot(time, trend_est, 'r-', label='Trend')
ax.plot(time, full_seasonal, 'g-', label='Seasonality')
ax.plot(time, residual, 'gray', alpha=0.5, label='Residual')
ax.set_title('Seasonality Decomposition')
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase58', exist_ok=True)
plt.savefig('src/phase58/time_series_forecasting.png', dpi=150)
print("\nSaved plot to src/phase58/time_series_forecasting.png")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Moving Average (window=12) MAE:     {ma_mae:.3f}")
print(f"Exponential Smoothing (α={best_alpha}) MAE:  {es_mae:.3f}")
print(f"Autoregressive AR(3) MAE:           {ar_mae:.3f}")
print("\nTime series forecasting:")
print("  - Autocorrelation reveals dependence on past values")
print("  - Moving average smooths noise but lags behind trends")
print("  - Exponential smoothing weights recent observations more")
print("  - AR models capture momentum using past values directly")
print("  - Decomposition separates trend, seasonality, and noise")
print("\nApplications: finance, weather, operations, healthcare")
