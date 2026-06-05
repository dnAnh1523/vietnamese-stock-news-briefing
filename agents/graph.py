"""LangGraph graph - orchestration logic."""

from langgraph.graph import StateGraph, END
from config import MAX_RETRIES
from agents.state import AgentState
from agents.scraper_agent import scraper_agent
from agents.analyst_agent import analyst_agent
from agents.price_agent import price_agent
from agents.report_agent import report_agent


def route_after_analyst(state: AgentState) -> str:
    if state.get("need_more_data") and state["retry_count"] < MAX_RETRIES:
        return "scraper"
    if state.get("need_price_data") and not state.get("price_context"):
        return "price"
    return "report"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("scraper", scraper_agent)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("price", price_agent)
    graph.add_node("report", report_agent)

    graph.set_entry_point("scraper")
    graph.add_edge("scraper", "analyst")
    graph.add_conditional_edges("analyst", route_after_analyst, {
        "scraper": "scraper",
        "price": "price",
        "report": "report",
    })
    graph.add_edge("price", "analyst")
    graph.add_edge("report", END)

    return graph.compile()
