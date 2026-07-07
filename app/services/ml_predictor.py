import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd


def predict_price(data: pd.DataFrame, days_ahead: int = 5) -> dict:
    """
    Train a Linear Regression model on historical closing prices
    and predict future price.

    Returns dict with predicted_price, trend, confidence_interval.
    """
    close_prices = data['Close'].dropna().values

    if len(close_prices) < 10:
        raise ValueError("Not enough data to train prediction model.")

    # Feature: day index
    X = np.arange(len(close_prices)).reshape(-1, 1)
    y = close_prices

    model = LinearRegression()
    model.fit(X, y)

    # Score
    r2 = model.score(X, y)

    # Predict next N days
    future_X = np.arange(len(close_prices), len(close_prices) + days_ahead).reshape(-1, 1)
    future_prices = model.predict(future_X)
    predicted_price = float(future_prices[-1])

    # Trend based on slope
    slope = model.coef_[0]
    trend = "UP" if slope > 0 else "DOWN"

    # Residuals for uncertainty
    residuals = y - model.predict(X)
    std_err = float(np.std(residuals))

    # Predicted prices for chart (last 30 days + next 5)
    chart_X = np.arange(max(0, len(close_prices) - 30), len(close_prices) + days_ahead).reshape(-1, 1)
    chart_predictions = model.predict(chart_X).tolist()

    return {
        "predicted_price": round(predicted_price, 2),
        "trend": trend,
        "slope": round(float(slope), 4),
        "r2_score": round(float(r2), 4),
        "std_err": round(std_err, 2),
        "lower_bound": round(predicted_price - std_err, 2),
        "upper_bound": round(predicted_price + std_err, 2),
        "chart_predictions": [round(p, 2) for p in chart_predictions],
        "model_accuracy": round(float(r2) * 100, 1),
    }
