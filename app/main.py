from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import engine, Base
from app.routers import auth, analysis

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="TradeCortex API",
    description="AI-powered stock analysis platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(analysis.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ TradeCortex API started")
    print("📖 Swagger docs: http://localhost:8000/docs")


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"} 
