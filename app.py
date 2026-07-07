from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from flask_session import Session
from services.stock_service import get_stock_data, get_stock_info
from services.news_service import get_news
from services.sentiment import analyze_sentiment
from services.volatility import calculate_volatility, calculate_evs
from services.recommendation import get_recommendation
from services.explanation import generate_explanation
from services.db_service import save_report, get_recent_reports, init_db
from services.ml_predictor import predict_price
from auth_routes import auth_bp, init_users_table   # ← NEW
import traceback
import os

app = Flask(__name__)
CORS(app)

# ── Secret key for sessions ──────────────────────────────────────────
# Change this to a long random string in production!
app.secret_key = os.getenv("SECRET_KEY", "tradecortex-super-secret-key-change-me-2024")

# ── Configure Flask-Session ──────────────────────────────────────────
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# ── Register auth blueprint ──────────────────────────────────────────
app.register_blueprint(auth_bp)

# ── Initialize databases on startup ─────────────────────────────────
try:
    db_ok = init_db()
    print(f"✅ Stock reports table initialized: {db_ok}")
except Exception as e:
    print(f"⚠️  DB init failed (app will still run): {e}")

try:
    users_ok = init_users_table()
    print(f"✅ Users table initialized: {users_ok}")
except Exception as e:
    print(f"⚠️  Users table init failed: {e}")


# ── ROOT — redirect to login or dashboard ────────────────────────────
@app.route('/')
def index():
    from flask import session
    if "user_id" in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login_page'))


# ── MAIN ANALYSIS ROUTE ──────────────────────────────────────────────
@app.route('/api/analyze', methods=['GET'])
def analyze():
    symbol = request.args.get('symbol', 'AAPL').upper().strip()
    investor_type = request.args.get('investor_type', 'moderate').lower()

    try:
        # 1. Stock Data
        data = get_stock_data(symbol)
        latest_price = float(data['Close'].iloc[-1])
        previous_price = float(data['Close'].iloc[-5]) if len(data) >= 5 else float(data['Close'].iloc[0])
        trend = "UP" if latest_price > previous_price else "DOWN"

        # Price history for chart (last 60 days)
        price_history = data['Close'].tail(60).round(2).tolist()
        date_labels = data.tail(60).index.strftime('%b %d').tolist()

        # 2. ML Prediction
        ml_result = predict_price(data, days_ahead=5)
        predicted_price = ml_result["predicted_price"]
        ml_trend = ml_result["trend"]

        # Extend labels for prediction
        from datetime import timedelta
        import pandas as pd
        last_date = data.index[-1]
        future_labels = [(last_date + timedelta(days=i+1)).strftime('%b %d') for i in range(5)]
        prediction_labels = date_labels[-30:] + future_labels

        # 3. News & Sentiment
        news = get_news(symbol)
        sentiment_score, sentiment_label = analyze_sentiment(news)

        # 4. Volatility
        volatility, risk = calculate_volatility(ml_trend, sentiment_score)
        confidence = max(0, round((1 - volatility) * 100, 2))

        # 5. EVS (Emotional Volatility Score)
        evs_data = calculate_evs(data, sentiment_score, ml_trend)

        # 6. Recommendation
        recommendation = get_recommendation(sentiment_label, risk, investor_type, ml_trend)

        # 7. Explanation
        explanation = generate_explanation(
            sentiment_label, risk, recommendation,
            trend=ml_trend, investor_type=investor_type,
            evs_level=evs_data["evs_level"],
            predicted_price=predicted_price,
            current_price=latest_price,
        )

        # 8. Stock info
        try:
            stock_info = get_stock_info(symbol)
        except Exception:
            stock_info = {"name": symbol, "sector": "N/A", "market_cap": 0, "pe_ratio": 0}

        # 9. Save to DB
        report_id = None
        try:
            report_id = save_report(
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
        except Exception as e:
            print(f"DB save warning: {e}")

        return jsonify({
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
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def history():
    """Get recent analysis reports."""
    try:
        reports = get_recent_reports(limit=20)
        return jsonify({"success": True, "reports": reports})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)