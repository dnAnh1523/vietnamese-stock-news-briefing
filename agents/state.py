"""Shared state cho LangGraph agents."""

from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    ticker: str
    articles: List[dict]
    price_context: Optional[dict]
    analysis: Optional[str]
    need_more_data: bool
    need_price_data: bool
    retry_count: int
    final_report: Optional[dict]
