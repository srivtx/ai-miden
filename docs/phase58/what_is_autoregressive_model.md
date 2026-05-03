## What Is an Autoregressive Model?

---

### The Problem

You have a time series where each value depends on previous values. Temperature today is correlated with temperature yesterday. Stock price today depends on prices from the past week. How do you build a model that uses the series' own past values to predict its future?

---

### Definition

An **autoregressive (AR) model** predicts the next value in a time series as a linear combination of the previous p values, plus noise.

**The AR(p) formula:**
```
x_t = c + φ_1 * x_{t-1} + φ_2 * x_{t-2} + ... + φ_p * x_{t-p} + ε_t
```

Where:
- `x_t` = value at time t
- `c` = constant (mean level)
- `φ_1...φ_p` = autoregressive coefficients (how much each past value matters)
- `p` = number of lagged terms (order of the model)
- `ε_t` = white noise (random error, mean 0)

**Key insight:**
- AR models capture the "momentum" in a time series
- If φ_1 is close to 1, the series has strong inertia (tomorrow ≈ today)
- If all φ are close to 0, the series is white noise (no predictable pattern)

**Why this matters:**
- AR is the foundation of ARIMA, the most widely used time series model
- It formalizes the intuition that "the past predicts the future"
- Even simple AR(1) models can capture meaningful trends

---

### Real-Life Analogy

A pendulum.
- **AR(1):** The pendulum's position at time t depends mainly on its position at t-1 (inertia carries it forward). If φ_1 = 0.9, it slowly decays: each swing is 90% of the previous.
- **AR(2):** The pendulum also depends on t-2 (the restoring force from two steps ago). This captures the oscillation better.
- **White noise (φ=0):** The pendulum is hit by random gusts of wind every second. Its position is completely unpredictable.

The autoregressive coefficients are like the physics constants of the pendulum: they determine how the system evolves from its own past state.

---

### Tiny Numeric Example

**AR(1) model:** `x_t = 5 + 0.7 * x_{t-1} + ε_t`

**Generate a series:**
```
x_0 = 10
x_1 = 5 + 0.7*10 + 0 = 12
x_2 = 5 + 0.7*12 + 0 = 13.4
x_3 = 5 + 0.7*13.4 + 0 = 14.38
x_4 = 5 + 0.7*14.38 + 0 = 15.07
```

The series converges toward a mean. With noise:
```
x_1 = 5 + 0.7*10 + 0.5 = 12.5
x_2 = 5 + 0.7*12.5 - 0.3 = 13.45
x_3 = 5 + 0.7*13.45 + 0.2 = 14.62
```

**Forecasting:**
```
Given x_10 = 15, predict x_11:
x_11 = 5 + 0.7*15 = 15.5

Predict x_12 (using the prediction for x_11):
x_12 = 5 + 0.7*15.5 = 15.85
```

Forecasts gradually converge to the long-term mean: `c / (1 - φ_1) = 5 / 0.3 = 16.67`

---

### Common Confusion

1. **"AR models only work for stationary series."** True for AR alone. But differencing (ARIMA) handles non-stationary trends.

2. **"Higher p is always better."** No. AR(10) with tiny coefficients overfits. Use AIC/BIC to select p.

3. **"AR is outdated because of LSTMs."** AR and ARIMA still win on small datasets and are interpretable. LSTMs need more data.

4. **"AR models cannot capture seasonality."** True for basic AR. Seasonal ARIMA (SARIMA) adds seasonal terms.

5. **"The coefficients must sum to less than 1."** For stationarity, yes. But non-stationary series can still be modeled with differencing.

---

### Where It Is Used in Our Code

`src/phase58/phase58_time_series_forecasting.py` — We fit an AR(3) model to a synthetic time series by solving for the optimal coefficients using least squares, then use it to forecast future values.
