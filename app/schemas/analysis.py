from pydantic import BaseModel
from typing import Literal, Optional


class AnalyzeRequest(BaseModel):
    symbol: str
    investor_type: Literal["conservative", "moderate", "aggressive"] = "moderate"


class PriceInfo(BaseModel):
    current: float
    previous: float
    change: float
    change_pct: float
    trend: str


class MLPrediction(BaseModel):
    predicted_price: float
    trend: str
    model_accuracy: float
    r2_score: float
    lower_bound: float
    upper_bound: float


class SentimentInfo(BaseModel):
    label: str
    score: float
    news: list[str]


class VolatilityInfo(BaseModel):
    score: float
    risk: str
    confidence: float


class EVSInfo(BaseModel):
    evs_score: float
    evs_level: str
    evs_description: str
    price_volatility: float
    mismatch_factor: float


class StockInfo(BaseModel):
    name: str
    sector: str
    market_cap: float
    pe_ratio: float


class ChartData(BaseModel):
    dates: list[str]
    prices: list[float]
    prediction_dates: list[str]
    prediction_prices: list[float]


class AnalyzeResponse(BaseModel):
    success: bool
    symbol: str
    stock_info: StockInfo
    price: PriceInfo
    ml_prediction: MLPrediction
    sentiment: SentimentInfo
    volatility: VolatilityInfo
    evs: EVSInfo
    recommendation: str
    explanation: str
    investor_type: str
    chart_data: ChartData
    report_id: Optional[int] = None


class ReportListItem(BaseModel):
    id: int
    symbol: str
    price: float
    recommendation: str
    sentiment_label: str
    risk_level: str
    created_at: str

    class Config:
        from_attributes = True 
