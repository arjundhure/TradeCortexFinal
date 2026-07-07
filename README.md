# TradeCortex 📈

AI-powered full-stack stock analysis platform built with FastAPI, PostgreSQL, Redis, and React.

## Features
- 🔐 JWT authentication (access + refresh tokens)
- 📊 Real-time stock analysis with ML price prediction
- ⚡ EVS (Emotional Volatility Score) — unique sentiment-price mismatch indicator
- 📰 NLP news sentiment analysis
- 🔴 WebSocket live price feeds
- 📈 Side-by-side stock comparison
- 🗄️ PostgreSQL + SQLAlchemy ORM + Alembic migrations
- ⚡ Redis caching (60s TTL on stock data)

## Tech Stack

### Backend
- FastAPI + Uvicorn
- PostgreSQL + SQLAlchemy + Alembic
- Redis caching
- JWT auth (python-jose + bcrypt)
- scikit-learn ML prediction
- yfinance + TextBlob sentiment analysis

### Frontend
- React + Vite
- TanStack React Query
- Zustand state management
- Recharts
- Axios with JWT interceptors
- WebSockets for live price feeds

## Setup

### Backend
```bash
cd TradeCortex
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in DATABASE_URL, REDIS_URL, SECRET_KEY in .env
python run.py
```

### Frontend
```bash
cd tradecortex-ui
npm install
npm run dev
```

## API Documentation
Run the backend and open:
http://localhost:8000/docs
Interactive Swagger UI with all endpoints.

## Pages
| Page | Description |
|------|-------------|
| Dashboard | Overview + recent analyses |
| Analyze | Full AI analysis — chart, EVS gauge, sentiment, ML prediction, recommendation |
| Compare | Side-by-side stock comparison |
| History | Past analyses table with PostgreSQL data |

## Architecture
Request → FastAPI → JWT middleware → Redis cache check
↓ miss
yfinance + ML + Sentiment + EVS
↓
PostgreSQL (SQLAlchemy ORM)
↓
Redis cache (60s TTL) → JSON response
