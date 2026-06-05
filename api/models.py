"""Pydantic models for API request/response."""

from typing import Optional

from pydantic import BaseModel, Field


class KeyEvent(BaseModel):
    date: Optional[str] = None
    title: str
    impact: str = "low"


class BriefingResponse(BaseModel):
    ticker: str
    period: str
    summary: str
    key_events: list[KeyEvent] = Field(default_factory=list)
    impact_level: str
    risk_flags: list[str] = Field(default_factory=list)
    opportunity_flags: list[str] = Field(default_factory=list)
