## What Is Seasonality Decomposition?

---

### The Problem

A time series often contains multiple overlapping patterns: a long-term upward trend, a repeating weekly cycle, and random day-to-day noise. If you try to forecast the raw series, these patterns fight each other. How do you separate the signal from the noise and model each component independently?

---

### Definition

**Seasonality decomposition** is the process of splitting a time series into its constituent components: trend, seasonality, and residual (noise).

**Additive model:**
```
x_t = Trend_t + Seasonal_t + Residual_t
```

**Multiplicative model:**
```
x_t = Trend_t × Seasonal_t × Residual_t
```

**Components:**
- **Trend:** Long-term direction (moving average over a long window)
- **Seasonality:** Repeating pattern (average deviation for each season, e.g., Monday = +5, Tuesday = -3)
- **Residual:** What's left after removing trend and seasonality (should look like random noise)

**Why this matters:**
- Decomposition reveals hidden patterns
- You can model each component separately (trend with linear regression, seasonality with dummy variables)
- It is the first step in any serious time series analysis

---

### Real-Life Analogy

A symphony orchestra.
- **The full series:** The complete sound of all instruments playing together
- **Trend:** The underlying melody played by the violins (long-term direction)
- **Seasonality:** The repeating rhythm section (weekly drum pattern)
- **Residual:** The random squeaks, coughs, and ambient noise

Decomposition is like using a mixing board to isolate each instrument. Once separated, you can study the melody without the drums, or analyze the rhythm without the melody.

---

### Tiny Numeric Example

**Monthly sales data:**
```
Month: 1   2   3   4   5   6   7   8   9  10  11  12
Sales: 12  15  18  16  20  23  21  25  28  26  30  33
```

**Step 1: Estimate trend (2-month moving average):**
```
Trend:  -   13.5  16.5  17  18  21.5  22  23  26.5  27  28  31.5
```

**Step 2: Detrend (actual - trend):**
```
Detrended: -  1.5   1.5  -1   2   1.5  -1   2   1.5  -1   2   1.5
```

**Step 3: Estimate seasonality (average detrended values for each month):**
```
Assuming yearly seasonality with only 1 year of data,
we see a pattern: odd months +1.5, even months -1 to +2
```

**Step 4: Compute residual:**
```
Residual = Actual - Trend - Seasonal
```

**Result:**
```
Sales = Trend + Seasonal + Residual
33    = 31.5   + 1.5      + 0.0
```

The decomposition separates the long-term growth (trend) from the monthly pattern (seasonality) from random fluctuations (residual).

---

### Common Confusion

1. **"Trend and seasonality are the same."** No. Trend is long-term direction. Seasonality is repeating short-term cycles.

2. **"You can always use additive decomposition."** Use multiplicative when seasonal fluctuations grow with the trend (e.g., sales double in December as the business grows).

3. **"Residual should be exactly zero."** No. Residual is the unpredictable part. It should look like random noise, not be zero.

4. **"Decomposition requires deep learning."** No. Classical methods (moving averages, STL decomposition) work well and are interpretable.

5. **"Once decomposed, you forecast each component separately."** Yes, then add/multiply them back together for the final forecast.

---

### Where It Is Used in Our Code

`src/phase58/phase58_time_series_forecasting.py` — We decompose a synthetic time series into trend, seasonality, and residual using moving averages, then visualize each component separately and recompose them to verify the decomposition.
