def get_recommendation(sentiment_label: str, risk: str, investor_type: str = "moderate", trend: str = "UP") -> str:
    """
    Smart recommendation engine based on ML prediction, sentiment, EVS, and investor type.
    """
    investor_type = investor_type.lower()

    # Base score system
    score = 0

    # Trend contribution
    if trend == "UP":
        score += 2
    else:
        score -= 2

    # Sentiment contribution
    if sentiment_label == "Positive":
        score += 2
    elif sentiment_label == "Negative":
        score -= 2

    # Risk contribution
    if risk == "Low":
        score += 1
    elif risk == "Medium":
        score += 0
    elif risk == "High":
        score -= 2

    # Investor type adjustments
    if investor_type == "conservative":
        # Needs very strong buy signals
        if score >= 4:
            return "Buy"
        elif score >= 1:
            return "Hold"
        else:
            return "Sell"
    elif investor_type == "aggressive":
        # More willing to take risks
        if score >= 1:
            return "Buy"
        elif score >= -1:
            return "Hold"
        else:
            return "Sell"
    else:  # moderate
        if score >= 3:
            return "Buy"
        elif score >= 0:
            return "Hold"
        else:
            return "Sell"
