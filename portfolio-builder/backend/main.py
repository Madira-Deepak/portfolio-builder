import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Load .env from the same folder as this file — works no matter where you run uvicorn from
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
    print(f"[startup] Loading .env from: {env_path}")
    print(f"[startup] GROQ_API_KEY loaded: {bool(os.environ.get('GROQ_API_KEY'))}")
except ImportError:
    print("[startup] python-dotenv not installed, skipping .env load")

from models.schema import PortfolioRequest, PortfolioResponse
from services.ai_service import generate_portfolio

app = FastAPI(
    title="Portfolio Builder API",
    description="AI-powered portfolio generation using Groq (free)",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Portfolio Builder API is running",
        "version": "3.0.0",
        "model": "llama-3.3-70b (Groq — free)",
        "api_key_configured": bool(os.environ.get("GROQ_API_KEY")),
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "api_key_configured": bool(os.environ.get("GROQ_API_KEY")),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/generate", response_model=PortfolioResponse)
def generate(data: PortfolioRequest):
    try:
        content = generate_portfolio(data)
        return PortfolioResponse(
            content=content,
            style=data.style or "modern",
            generated_at=datetime.utcnow().isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")