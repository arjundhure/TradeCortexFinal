import numpy as np
import pandas as pd


def calculate_volatility(trend: str, sentiment_score: float) -> tuple:
    """
    Calculate volatility score.
    Returns (volatility_score, risk_level).
    """
    # Base volatility from sentiment magnitude
    sentiment_volatility = abs(sentiment_score)

    # Mismatch: price going up but negative sentiment = higher risk
    if trend == "UP" and sentiment_score < 0:
        mismatch_penalty = 0.3
    elif trend == "DOWN" and sentiment_score > 0:
        mismatch_penalty = 0.2
    else:
        mismatch_penalty = 0.0

    volatility = min(1.0, sentiment_volatility + mismatch_penalty + 0.1)

    if volatility < 0.3:
        risk = "Low"
    elif volatility < 0.6:
        risk = "Medium"
    else:
        risk = "High"

    return volatility, risk


def calculate_evs(data: pd.DataFrame, sentiment_score: float, trend: str) -> dict:
    """
    Emotional Volatility Score (EVS) - unique USP feature.
    Combines price volatility with sentiment mismatch.
    """
    close_prices = data['Close'].dropna().values

    # Price-based volatility (standard deviation of returns)
    returns = np.diff(close_prices) / close_prices[:-1]
    price_volatility = float(np.std(returns)) if len(returns) > 1 else 0.1

    # Normalize to 0-1
    price_vol_normalized = min(1.0, price_volatility * 10)

    # Sentiment component
    sentiment_component = (1 - sentiment_score) / 2  # map -1..1 to 1..0

    # Mismatch factor
    if trend == "UP" and sentiment_score < -0.1:
        mismatch = 0.4  # High mismatch: price up, news bad
    elif trend == "DOWN" and sentiment_score > 0.1:
        mismatch = 0.3  # Moderate mismatch: price down, news good
    elif trend == "UP" and sentiment_score > 0.1:
        mismatch = 0.0  # Aligned: price up, news good
    else:
        mismatch = 0.1  # Slight uncertainty

    # EVS = weighted combination
    evs = (price_vol_normalized * 0.4) + (sentiment_component * 0.35) + (mismatch * 0.25)
    evs = min(1.0, max(0.0, evs))

    if evs < 0.33:
        evs_level = "Low"
        evs_description = "Market sentiment aligns with price action. Lower uncertainty."
    elif evs < 0.66:
        evs_level = "Medium"
        evs_description = "Some disconnect between price movement and sentiment. Exercise caution."
    else:
        evs_level = "High"
        evs_description = "Strong sentiment-price mismatch detected. High emotional volatility."

    return {
        "evs_score": round(evs * 100, 1),
        "evs_level": evs_level,
        "evs_description": evs_description,
        "price_volatility": round(price_vol_normalized * 100, 1),
        "mismatch_factor": round(mismatch * 100, 1),
    }
