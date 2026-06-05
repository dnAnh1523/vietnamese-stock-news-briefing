import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agents.graph import build_graph
from api.models import BriefingResponse
from crawlers.vnstock_fetcher import VnstockFetcher

load_dotenv()
logger = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = FastAPI(
    title="Vietnamese Stock News Briefing API",
    description="Analyze stock news and generate actionable briefings",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()
ticker_validator = VnstockFetcher()

TICKER_PATTERN = re.compile(r"^[A-Z0-9]{1,10}$")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
    }


@app.post("/analyze", response_model=BriefingResponse)
async def analyze(ticker: str = Query(..., description="Mã cổ phiếu, VD: HPG")):
    ticker = ticker.strip().upper()

    if not ticker:
        raise HTTPException(status_code=400, detail="ticker is required")

    if not TICKER_PATTERN.match(ticker):
        raise HTTPException(status_code=400, detail="Mã cổ phiếu không hợp lệ")

    if not ticker_validator.is_valid_ticker(ticker):
        raise HTTPException(
            status_code=404,
            detail=f"Mã {ticker} không tồn tại trên HOSE/HNX/UPCOM",
        )

    initial_state = {
        "ticker": ticker,
        "articles": [],
        "price_context": None,
        "analysis": None,
        "need_more_data": False,
        "need_price_data": False,
        "retry_count": 0,
        "final_report": None,
    }

    try:
        result = graph.invoke(initial_state)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.exception("Graph execution failed for %s", ticker)
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {e}") from e

    if result.get("final_report") is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đủ tin tức để phân tích",
        )

    return result["final_report"]


@app.get("/")
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
