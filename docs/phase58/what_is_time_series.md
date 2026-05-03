## What Is a Time Series?

---

### The Problem

Stock prices, weather, heartbeats, website traffic, electricity demand — these are all sequences of measurements taken over time. But unlike text or audio, time series have unique properties: trends, seasons, and correlations with their own past values. How do you predict the next value when the pattern depends on what happened yesterday, last week, and last year?

---

### Definition

A **time series** is a sequence of data points recorded at successive, equally spaced time intervals. Time series forecasting is the task of predicting future values based on past observations.

**Key properties:**
- **Temporal ordering matters:** You cannot shuffle the data
- **Autocorrelation:** Today's value depends on yesterday's value
- **Trend:** Long-term direction (upward, downward, flat)
- **Seasonality:** Repeating patterns at fixed intervals (daily, weekly, yearly)
- **Stationarity:** Whether statistical properties (mean, variance) change over time

**Examples:**
- **Finance:** Predicting stock prices from historical trading data
- **Weather:** Forecasting temperature from past meteorological readings
- **Healthcare:** Predicting patient deterioration from vital signs
- **Operations:** Forecasting server load to auto-scale cloud resources

**Why this matters:**
- Time series data is everywhere in the real world
- Standard machine learning (random shuffling) destroys temporal structure
- Specialized techniques are needed to capture trends and seasonality

---

### Real-Life Analogy

A farmer planning harvests.
- **The time series:** Daily temperature readings for the past 5 years
- **Trend:** Climate change means temperatures are gradually rising
- **Seasonality:** Every summer is hot, every winter is cold
- **Autocorrelation:** If today is 25°C, tomorrow is likely 24-26°C, not 5°C
- **Forecasting:** The farmer uses the past 5 years to predict when to plant crops this year

Ignoring temporal structure would be like shuffling the temperature readings and trying to predict summer from a random winter day.

---

### Tiny Numeric Example

**Daily temperature readings (°C):**
```
Day:  1   2   3   4   5   6   7   8   9  10
Temp: 20  21  19  22  20  21  23  22  20  24
```

**Autocorrelation (correlation with previous day):**
```
Lag-1: correlation([20,21,19,22,20,21,23,22,20], [21,19,22,20,21,23,22,20,24]) = 0.35
```

Weak positive correlation — warm days tend to follow warm days.

**Trend (linear fit):**
```
Slope = +0.35°C per day (gradually warming)
```

**Forecast (naive — assume tomorrow = today):**
```
Day 11 prediction: 24°C (same as day 10)
Actual: 23°C
Error: 1°C
```

**Forecast (moving average of last 3 days):**
```
Day 11 prediction: (22 + 20 + 24) / 3 = 22°C
Error: |23 - 22| = 1°C
```

Simple baselines often work surprisingly well.

---

### Common Confusion

1. **"Time series is just regression with time as a feature."** No. Time is not an independent variable. The dependence on past values creates autocorrelation that violates standard regression assumptions.

2. **"You can shuffle time series data."** Never. Shuffling destroys the temporal structure and makes the task meaningless.

3. **"More data always helps."** For time series, recent data often matters more than old data. Data from 10 years ago may be irrelevant if the system has changed.

4. **"Stationarity is required."** Many models assume stationarity, but real-world data is rarely stationary. Techniques like differencing and detrending are used to make it stationary.

5. **"Deep learning beats everything for time series."** Not always. ARIMA and exponential smoothing often beat LSTMs on small datasets. Deep learning shines on large, complex, multivariate series.

---

### Where It Is Used in Our Code

`src/phase58/phase58_time_series_forecasting.py` — We generate a synthetic time series with trend and seasonality, then forecast future values using moving averages, exponential smoothing, and an autoregressive model.
