"""Agent logic tests."""

import json

from agents.graph import route_after_analyst
from agents.report_agent import report_agent
from prompts.analyst_prompt import build_user_prompt


def test_route_after_analyst_needs_more_data():
    state = {
        "ticker": "HPG",
        "articles": [],
        "price_context": None,
        "analysis": None,
        "need_more_data": True,
        "need_price_data": False,
        "retry_count": 1,
        "final_report": None,
    }
    assert route_after_analyst(state) == "scraper"


def test_route_after_analyst_needs_price():
    state = {
        "ticker": "HPG",
        "articles": [{"Title": "a"}] * 5,
        "price_context": None,
        "analysis": None,
        "need_more_data": False,
        "need_price_data": True,
        "retry_count": 1,
        "final_report": None,
    }
    assert route_after_analyst(state) == "price"


def test_route_after_analyst_to_report():
    state = {
        "ticker": "HPG",
        "articles": [{"Title": "a"}] * 5,
        "price_context": {"latest_close": 25000},
        "analysis": "{}",
        "need_more_data": False,
        "need_price_data": False,
        "retry_count": 1,
        "final_report": None,
    }
    assert route_after_analyst(state) == "report"


def test_report_agent_handles_none_analysis():
    state = {
        "ticker": "HPG",
        "articles": [{"Title": "Test", "SubTitle": "sub"}],
        "price_context": None,
        "analysis": None,
        "need_more_data": False,
        "need_price_data": False,
        "retry_count": 1,
        "final_report": None,
    }
    result = report_agent(state)
    assert result["final_report"]["impact_level"] == "None"
    assert result["final_report"]["ticker"] == "HPG"


def test_report_agent_parses_json_analysis():
    analysis = json.dumps({
        "summary": "Tóm tắt",
        "key_events": ["Sự kiện A", {"date": "2026-06-01", "title": "Sự kiện B", "impact": "high"}],
        "impact_level": "medium",
        "risk_flags": ["Rủi ro 1"],
        "opportunity_flags": ["Cơ hội 1"],
    })
    state = {
        "ticker": "HPG",
        "articles": [{"Title": "Test"}],
        "price_context": None,
        "analysis": analysis,
        "need_more_data": False,
        "need_price_data": False,
        "retry_count": 1,
        "final_report": None,
    }
    result = report_agent(state)
    report = result["final_report"]
    assert report["summary"] == "Tóm tắt"
    assert len(report["key_events"]) == 2
    assert report["key_events"][1]["impact"] == "high"


def test_build_user_prompt_accepts_price_context():
    prompt = build_user_prompt(
        "HPG",
        "Article text",
        {"latest_close": 25000, "week_change_pct": 1.5},
    )
    assert "Article text" in prompt
    assert "latest_close" in prompt
    assert "25000" in prompt
