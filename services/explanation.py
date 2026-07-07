def generate_explanation(sentiment_label: str, risk: str, recommendation: str,
                          trend: str = "UP", investor_type: str = "moderate",
                          evs_level: str = "Medium", predicted_price: float = 0,
                          current_price: float = 0) -> str:
    """
    Generate human-readable explanation for the AI recommendation.
    """
    parts = []

    # Price trend
    if trend == "UP":
        parts.append("📈 Price trend is upward")
    else:
        parts.append("📉 Price trend is downward")

    # Sentiment
    if sentiment_label == "Positive":
        parts.append("😊 news sentiment is positive")
    elif sentiment_label == "Negative":
        parts.append("😟 news sentiment is negative")
    else:
        parts.append("😐 news sentiment is neutral")

    # EVS
    if evs_level == "High":
        parts.append("⚠️ high emotional volatility detected (price-sentiment mismatch)")
    elif evs_level == "Medium":
        parts.append("🔶 moderate emotional volatility observed")
    else:
        parts.append("✅ low emotional volatility (aligned signals)")

    # Risk
    parts.append(f"risk level is {risk.lower()}")

    # Investor context
    investor_map = {
        "conservative": "conservative strategy prioritizes capital safety",
        "moderate": "moderate strategy balances risk and reward",
        "aggressive": "aggressive strategy accepts higher risk for potential gains",
    }
    parts.append(investor_map.get(investor_type.lower(), "balanced approach applied"))

    # Prediction
    if predicted_price and current_price:
        delta = predicted_price - current_price
        pct = (delta / current_price) * 100 if current_price else 0
        if delta > 0:
            parts.append(f"ML model predicts +{abs(pct):.1f}% price increase to ${predicted_price}")
        else:
            parts.append(f"ML model predicts -{abs(pct):.1f}% price decrease to ${predicted_price}")

    # Build explanation
    explanation_body = ", ".join(parts[:-1]) + f", and {parts[-1]}."
    explanation = f"Analysis shows {explanation_body}"

    # Recommendation rationale
    rationale_map = {
        "Buy": "All key indicators support entry — this presents a favorable buying opportunity.",
        "Sell": "Risk factors outweigh upside potential — consider exiting the position.",
        "Hold": "Mixed signals suggest maintaining current position and monitoring closely.",
    }

    return f"{explanation} {rationale_map.get(recommendation, '')}"
