from textblob import TextBlob

def analyze_sentiment(news_headlines: list) -> tuple:
    """
    Analyze sentiment of news headlines using TextBlob.
    Returns (score, label) where score is -1 to 1.
    """
    if not news_headlines:
        return 0.0, "Neutral"

    total_score = 0.0
    for headline in news_headlines:
        blob = TextBlob(headline)
        total_score += blob.sentiment.polarity

    avg_score = total_score / len(news_headlines)

    if avg_score > 0.1:
        label = "Positive"
    elif avg_score < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return avg_score, label
