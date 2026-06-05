"""Report Agent - tổng hợp báo cáo cuối."""

import json
import logging
import re
from datetime import datetime, timedelta, timezone

from config import DEFAULT_DAYS
from agents.state import AgentState

logger = logging.getLogger(__name__)


def _parse_analysis(analysis_text: str | None) -> dict:
    if not analysis_text:
        return {}

    cleaned = analysis_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Failed to parse analysis JSON")
        return {}


def _normalize_key_events(events: list) -> list[dict]:
    normalized = []
    for event in events:
        if isinstance(event, dict):
            normalized.append({
                "date": event.get("date"),
                "title": event.get("title", ""),
                "impact": event.get("impact", "low"),
            })
        elif isinstance(event, str):
            normalized.append({"date": None, "title": event, "impact": "low"})
    return normalized


def report_agent(state: AgentState) -> AgentState:
    ticker = state["ticker"]
    articles = state.get("articles", [])
    analysis = _parse_analysis(state.get("analysis"))

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=DEFAULT_DAYS)
    period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    if not articles:
        final_report = {
            "ticker": ticker,
            "period": period,
            "summary": f"Không tìm thấy tin tức nào cho mã {ticker} trong {DEFAULT_DAYS} ngày gần nhất.",
            "key_events": [],
            "impact_level": "None",
            "risk_flags": [],
            "opportunity_flags": [],
        }
        return {**state, "final_report": final_report}

    if not analysis:
        final_report = {
            "ticker": ticker,
            "period": period,
            "summary": f"Không đủ tin tức để phân tích mã {ticker}.",
            "key_events": [],
            "impact_level": "None",
            "risk_flags": [],
            "opportunity_flags": [],
        }
        return {**state, "final_report": final_report}

    final_report = {
        "ticker": ticker,
        "period": period,
        "summary": analysis.get("summary", ""),
        "key_events": _normalize_key_events(analysis.get("key_events", [])),
        "impact_level": analysis.get("impact_level") or "None",
        "risk_flags": analysis.get("risk_flags", []),
        "opportunity_flags": analysis.get("opportunity_flags", []),
    }

    return {**state, "final_report": final_report}
