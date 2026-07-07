import yfinance as yf

MOCK_NEWS = {
    "AAPL": [
        "Apple reports record quarterly revenue driven by iPhone sales",
        "Apple Vision Pro faces supply chain challenges",
        "Apple stock hits all-time high amid AI integration buzz",
    ],
    "TSLA": [
        "Tesla deliveries disappoint Wall Street expectations",
        "Tesla unveils new Gigafactory expansion plans",
        "Elon Musk sells Tesla shares amid controversy",
    ],
    "GOOGL": [
        "Google AI surpasses human performance on multiple benchmarks",
        "Alphabet revenue grows 15% year over year",
        "Google faces antitrust scrutiny in EU markets",
    ],
    "MSFT": [
        "Microsoft Azure cloud revenue surges 30%",
        "Microsoft integrates AI across all Office products",
        "Microsoft acquires gaming studio for $2 billion",
    ],
    "AMZN": [
        "Amazon AWS dominates cloud market share",
        "Amazon Prime membership crosses 200 million globally",
        "Amazon faces regulatory pressure over marketplace practices",
    ],
}

DEFAULT_NEWS = [
    "Stock market shows mixed signals amid global uncertainty",
    "Investors cautious as inflation data comes in higher than expected",
    "Tech sector leads gains in today's trading session",
]

def get_news(symbol: str) -> list:
    """Fetch news headlines for a stock symbol."""
    try:
        ticker = yf.Ticker(symbol)
        news_data = ticker.news
        if news_data:
            headlines = []
            for article in news_data[:5]:
                content = article.get("content", {})
                title = content.get("title", "") if isinstance(content, dict) else ""
                if title:
                    headlines.append(title)
            if headlines:
                return headlines
    except Exception:
        pass

    # Fallback to mock news
    return MOCK_NEWS.get(symbol.upper(), DEFAULT_NEWS)
