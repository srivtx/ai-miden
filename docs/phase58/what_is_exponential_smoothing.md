## What Is Exponential Smoothing?

---

### The Problem

A simple moving average gives equal weight to all recent observations. But intuitively, yesterday's temperature should matter more than the temperature from 10 days ago. How do you create a forecast that weights recent observations more heavily than older ones?

---

### Definition

**Exponential smoothing** is a time series forecasting method that produces weighted averages of past observations, where the weights decay exponentially as the observations get older.

**Simple exponential smoothing:**
```
s_t = α * x_t + (1-α) * s_{t-1}

Forecast: x_{t+1} = s_t
```

Where:
- `s_t` = smoothed value at time t (the "level")
- `α` = smoothing factor between 0 and 1
- `x_t` = actual observation at time t

**Effect of α:**
- **α = 0.1:** Very smooth. Older observations matter a lot. Slow to react to changes.
- **α = 0.9:** Very responsive. Recent observations dominate. Follows noise closely.

**Holt's method (trend):**
```
Level: l_t = α * x_t + (1-α) * (l_{t-1} + b_{t-1})
Trend: b_t = β * (l_t - l_{t-1}) + (1-β) * b_{t-1}
Forecast: x_{t+h} = l_t + h * b_t
```

**Holt-Winters (trend + seasonality):**
```
Adds a seasonal component s_t with period m
Forecast: x_{t+h} = (l_t + h*b_t) * s_{t-m+h}
```

**Why this matters:**
- Exponential smoothing is the foundation of modern business forecasting
- It requires no training data beyond the series itself
- It adapts to changing conditions automatically

---

### Real-Life Analogy

A weather forecaster's memory.
- **Moving average:** The forecaster remembers the last 7 days equally. What happened 7 days ago matters as much as yesterday.
- **Exponential smoothing (α=0.3):** The forecaster remembers yesterday clearly (30% weight), the day before less clearly (21% weight), and a week ago barely (8% weight). Their forecast is a fading memory of the past.
- **High α (0.9):** The forecaster has short-term memory. They react instantly to yesterday's heatwave but forget last week's cold front.

Exponential smoothing is how humans naturally weight recent experience more than distant memory.

---

### Tiny Numeric Example

**Series:** `[10, 12, 11, 13, 12]`

**Simple exponential smoothing (α=0.3):**
```
s_1 = 0.3*10 + 0.7*10 = 10.0  (initialize s_0 = x_1)
s_2 = 0.3*12 + 0.7*10.0 = 10.6
s_3 = 0.3*11 + 0.7*10.6 = 10.72
s_4 = 0.3*13 + 0.7*10.72 = 11.40
s_5 = 0.3*12 + 0.7*11.40 = 11.58

Forecast for t=6: 11.58
```

**With α=0.8:**
```
s_1 = 10.0
s_2 = 0.8*12 + 0.2*10 = 11.6
s_3 = 0.8*11 + 0.2*11.6 = 11.12
s_4 = 0.8*13 + 0.2*11.12 = 12.62
s_5 = 0.8*12 + 0.2*12.62 = 12.12

Forecast for t=6: 12.12 (closer to recent values)
```

**Error comparison:**
```
Actual t=6: 14
α=0.3 error: |14 - 11.58| = 2.42
α=0.8 error: |14 - 12.12| = 1.88
```

Higher α is better when the series changes quickly.

---

### Common Confusion

1. **"Exponential smoothing requires exponential functions."** No. The name comes from the exponential decay of weights, not from using exp() in the formula.

2. **"It only works for flat series."** Simple smoothing does. But Holt's method handles trends, and Holt-Winters handles seasonality.

3. **"α is a hyperparameter you must tune."** Yes. Grid search or cross-validation on past data finds the best α.

4. **"It cannot forecast multiple steps ahead."** It can. For h steps ahead, the forecast is the last smoothed value (simple) or level + h*trend (Holt's).

5. **"Deep learning has replaced exponential smoothing."** For large datasets, yes. But for monthly sales with 2 years of history, exponential smoothing often wins.

---

### Where It Is Used in Our Code

`src/phase58/phase58_time_series_forecasting.py` — We implement simple exponential smoothing and Holt's trend method on a synthetic series, comparing different α values and visualizing how the smoothed curve lags or tracks the original data.
