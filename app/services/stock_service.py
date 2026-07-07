import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

MOCK_DATA = {
    "AAPL": {"base": 189.50, "name": "Apple Inc.", "sector": "Technology"},
    "TSLA": {"base": 175.20, "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
    "GOOGL": {"base": 172.30, "name": "Alphabet Inc.", "sector": "Communication Services"},
    "MSFT": {"base": 415.80, "name": "Microsoft Corporation", "sector": "Technology"},
    "AMZN": {"base": 186.40, "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
    "NVDA": {"base": 875.40, "name": "NVIDIA Corporation", "sector": "Technology"},
    "META": {"base": 502.30, "name": "Meta Platforms Inc.", "sector": "Communication Services"},
    "NFLX": {"base": 628.10, "name": "Netflix Inc.", "sector": "Communication Services"},
}

def _generate_mock_data(symbol: str) -> pd.DataFrame:
    config = MOCK_DATA.get(symbol.upper(), {"base": 100.0})
    base_price = config["base"]
    dates = pd.date_range(end=datetime.now(), periods=90, freq='B')
    np.random.seed(hash(symbol) % 2**31)
    returns = np.random.normal(0.0008, 0.018, len(dates))
    prices = base_price * np.exp(np.cumsum(returns))
    df = pd.DataFrame({
        'Open': prices * (1 - np.random.uniform(0, 0.005, len(dates))),
        'High': prices * (1 + np.random.uniform(0, 0.015, len(dates))),
        'Low':  prices * (1 - np.random.uniform(0, 0.015, len(dates))),
        'Close': prices,
        'Volume': np.random.randint(50_000_000, 150_000_000, len(dates)),
    }, index=dates)
    return df

def get_stock_data(symbol: str, period: str = "3mo") -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        if not data.empty:
            return data
    except Exception:
        pass
    return _generate_mock_data(symbol)

def get_stock_info(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if info:
            return {
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
            }
    except Exception:
        pass
    config = MOCK_DATA.get(symbol.upper(), {"name": symbol, "sector": "N/A"})
    return {"name": config.get("name", symbol), "sector": config.get("sector", "N/A"), "market_cap": 0, "pe_ratio": 0}
