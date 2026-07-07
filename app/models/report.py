from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class StockReport(Base):
    __tablename__ = "stock_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float)
    sentiment_label = Column(String(20))
    sentiment_score = Column(Float)
    volatility = Column(Float)
    risk_level = Column(String(20))
    recommendation = Column(String(20))
    explanation = Column(Text)
    predicted_price = Column(Float)
    evs_score = Column(Float)
    evs_level = Column(String(20))
    investor_type = Column(String(20))
    ml_accuracy = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
