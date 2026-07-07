from fastapi import WebSocket, WebSocketDisconnect
import asyncio

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Literal
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.report import StockReport
from app.middleware.auth import get_optional_user
from app.services.cache import cache_get, cache_set, stock_cache_key

from app.services.stock_service import get_stock_data, get_stock_info
from app.services.news_service import get_news
from app.services.sentiment import analyze_sentiment
from app.services.volatility import calculate_volatility, calculate_evs
from app.services.recommendation import get_recommendation
from app.services.explanation import generate_explanation
from app.services.ml_predictor import predict_price

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/analyze")
def analyze(
    request: Request,
    symbol: str = Query(default="AAPL"),
    investor_type: Literal["conservative", "moderate", "aggressive"] = Query(default="moderate"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    symbol = symbol.upper().strip()

    # Cache check
    cache_key = stock_cache_key(symbol)
    cached = cache_get(cache_key)
    if cached:
        sentiment_label = cached["sentiment"]["label"]
        risk = cached["volatility"]["risk"]
        ml_trend = cached["ml_prediction"]["trend"]
        cached["recommendation"] = get_recommendation(sentiment_label, risk, investor_type, ml_trend)
        cached["investor_type"] = investor_type
        return cached

    # Stock data
    data = get_stock_data(symbol)
    latest_price = float(data["Close"].iloc[-1])
    previous_price = float(data["Close"].iloc[-5]) if len(data) >= 5 else float(data["Close"].iloc[0])
    trend = "UP" if latest_price > previous_price else "DOWN"
    price_history = data["Close"].tail(60).round(2).tolist()
    date_labels = data.tail(60).index.strftime("%b %d").tolist()

    # ML prediction
    ml_result = predict_price(data, days_ahead=5)
    predicted_price = ml_result["predicted_price"]
    ml_trend = ml_result["trend"]
    last_date = data.index[-1]
    future_labels = [(last_date + timedelta(days=i + 1)).strftime("%b %d") for i in range(5)]
    prediction_labels = date_labels[-30:] + future_labels

    # News & sentiment
    news = get_news(symbol)
    sentiment_score, sentiment_label = analyze_sentiment(news)

    # Volatility
    volatility, risk = calculate_volatility(ml_trend, sentiment_score)
    confidence = max(0, round((1 - volatility) * 100, 2))

    # EVS
    evs_data = calculate_evs(data, sentiment_score, ml_trend)

    # Recommendation
    recommendation = get_recommendation(sentiment_label, risk, investor_type, ml_trend)

    # Explanation
    explanation = generate_explanation(
        sentiment_label, risk, recommendation,
        trend=ml_trend,
        investor_type=investor_type,
        evs_level=evs_data["evs_level"],
        predicted_price=predicted_price,
        current_price=latest_price,
    )

    # Stock info
    try:
        stock_info = get_stock_info(symbol)
    except Exception:
        stock_info = {"name": symbol, "sector": "N/A", "market_cap": 0, "pe_ratio": 0}

    # Save to DB
    report_id = None
    try:
        report = StockReport(
            user_id=current_user.id if current_user else None,
            symbol=symbol,
            price=round(latest_price, 2),
            sentiment_label=sentiment_label,
            sentiment_score=round(sentiment_score, 4),
            volatility=round(volatility, 4),
            risk_level=risk,
            recommendation=recommendation,
            explanation=explanation,
            predicted_price=predicted_price,
            evs_score=evs_data["evs_score"],
            evs_level=evs_data["evs_level"],
            investor_type=investor_type,
            ml_accuracy=ml_result["model_accuracy"],
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        report_id = report.id
    except Exception as e:
        print(f"DB save warning: {e}")
        db.rollback()

    # Build response
    result = {
        "success": True,
        "symbol": symbol,
        "stock_info": stock_info,
        "price": {
            "current": round(latest_price, 2),
            "previous": round(previous_price, 2),
            "change": round(latest_price - previous_price, 2),
            "change_pct": round(((latest_price - previous_price) / previous_price) * 100, 2),
            "trend": trend,
        },
        "ml_prediction": {
            "predicted_price": predicted_price,
            "trend": ml_trend,
            "model_accuracy": ml_result["model_accuracy"],
            "r2_score": ml_result["r2_score"],
            "lower_bound": ml_result["lower_bound"],
            "upper_bound": ml_result["upper_bound"],
        },
        "sentiment": {
            "label": sentiment_label,
            "score": round(sentiment_score, 4),
            "news": news[:5],
        },
        "volatility": {
            "score": round(volatility, 4),
            "risk": risk,
            "confidence": confidence,
        },
        "evs": evs_data,
        "recommendation": recommendation,
        "explanation": explanation,
        "investor_type": investor_type,
        "chart_data": {
            "dates": date_labels,
            "prices": price_history,
            "prediction_dates": prediction_labels,
            "prediction_prices": ml_result["chart_predictions"],
        },
        "report_id": report_id,
    }

    cache_set(cache_key, result)
    return result


@router.get("/history")
def history(
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    query = db.query(StockReport)
    if current_user:
        query = query.filter(StockReport.user_id == current_user.id)
    reports = query.order_by(StockReport.created_at.desc()).limit(limit).all()

    return {
        "success": True,
        "reports": [
            {
                "id": r.id,
                "symbol": r.symbol,
                "price": r.price,
                "recommendation": r.recommendation,
                "sentiment_label": r.sentiment_label,
                "risk_level": r.risk_level,
                "created_at": str(r.created_at),
            }
            for r in reports
        ],
    } 

@router.websocket("/ws/price/{symbol}")
async def price_websocket(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        while True:
            try:
                data = get_stock_data(symbol.upper())
                latest = float(data["Close"].iloc[-1])
                prev = float(data["Close"].iloc[-2]) if len(data) > 1 else latest
                change_pct = ((latest - prev) / prev) * 100
                await websocket.send_json({
                    "symbol": symbol.upper(),
                    "price": round(latest, 2),
                    "change_pct": round(change_pct, 2),
                    "trend": "UP" if latest > prev else "DOWN",
                })
            except Exception:
                pass
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass
