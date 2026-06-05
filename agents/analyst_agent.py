"""Analyst Agent - phân tích tin tức bằng LLM."""

import json
import logging
import os
import re

from dotenv import load_dotenv
from groq import Groq

from config import MIN_ARTICLES
from agents.state import AgentState
from prompts.analyst_prompt import SYSTEM_PROMPT, build_user_prompt
from prompts.format_prompt import FORMAT_SYSTEM, build_format_prompt

load_dotenv()
logger = logging.getLogger(__name__)

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY chưa được cấu hình trong .env")
        _client = Groq(api_key=api_key)
    return _client


def _call_llm(system: str, user: str, temperature: float = 0.3) -> str:
    response = _get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def _parse_json_response(text: str) -> dict | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def analyst_agent(state: AgentState) -> AgentState:
    articles = state["articles"]
    price_context = state.get("price_context")

    if len(articles) < MIN_ARTICLES:
        logger.info("Insufficient articles (%d < %d), requesting retry", len(articles), MIN_ARTICLES)
        return {**state, "need_more_data": True, "need_price_data": False}

    if not price_context:
        logger.info("Price context missing for %s, requesting vnstock fetch", state["ticker"])
        return {**state, "need_more_data": False, "need_price_data": True}

    articles_text = "\n\n".join([
        f"--- Bài {i + 1} ---\nTiêu đề: {a['Title']}\nTóm tắt: {a['SubTitle']}\nNội dung: {a.get('content', '')}"
        for i, a in enumerate(articles)
    ])

    try:
        reasoning = _call_llm(
            system=SYSTEM_PROMPT,
            user=build_user_prompt(state["ticker"], articles_text, price_context),
            temperature=0.3,
        )
        analysis = _call_llm(
            system=FORMAT_SYSTEM,
            user=build_format_prompt(state["ticker"], reasoning),
            temperature=0.0,
        )
    except Exception as e:
        logger.error("LLM call failed for %s: %s", state["ticker"], e)
        fallback = json.dumps({
            "summary": f"Không thể phân tích do lỗi LLM: {e}",
            "key_events": [],
            "impact_level": "None",
            "risk_flags": [],
            "opportunity_flags": [],
        }, ensure_ascii=False)
        return {
            **state,
            "analysis": fallback,
            "need_more_data": False,
            "need_price_data": False,
        }

    if _parse_json_response(analysis) is None:
        logger.warning("Invalid JSON from formatter, using reasoning fallback")
        analysis = json.dumps({
            "summary": reasoning[:500],
            "key_events": [],
            "impact_level": "None",
            "risk_flags": [],
            "opportunity_flags": [],
        }, ensure_ascii=False)

    return {
        **state,
        "analysis": analysis,
        "need_more_data": False,
        "need_price_data": False,
    }
