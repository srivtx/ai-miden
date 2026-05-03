## Phase 58: Time Series Forecasting

---

### What We Built

A synthetic time series with trend and seasonality, then forecasted the final 20 points using moving averages, exponential smoothing, and an autoregressive model. We also decomposed the series into its components.

### Key Results

- **Moving Average (window=12):** MAE = 1.261
- **Exponential Smoothing (α=0.9):** MAE = 0.526 (best)
- **Autoregressive AR(3):** MAE = 0.679
- **Lag-1 autocorrelation:** 0.887 (strong dependence on previous value)
- **Seasonality period:** 24 (confirmed by lag-24 autocorrelation peak)
- **Decomposition reconstruction error:** 0.000000 (perfect)

### Concepts Covered

| Term | File |
|---|---|
| Time Series | `what_is_time_series.md` |
| Autoregressive Model | `what_is_autoregressive_model.md` |
| Exponential Smoothing | `what_is_exponential_smoothing.md` |
| Seasonality Decomposition | `what_is_seasonality_decomposition.md` |

### Connection to Next Phase

Now that we can forecast sequences, how do we train models when data is scattered across many devices and cannot be centralized? Phase 59 covers **federated learning**.

### Files

- `docs/phase58/what_is_time_series.md`
- `docs/phase58/what_is_autoregressive_model.md`
- `docs/phase58/what_is_exponential_smoothing.md`
- `docs/phase58/what_is_seasonality_decomposition.md`
- `docs/phase58/SUMMARY.md`
- `src/phase58/phase58_time_series_forecasting.py`
- `src/phase58/time_series_forecasting.png`
