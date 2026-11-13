"""Shapes of the JSON the API accepts and returns. Pydantic checks them for us."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

Level = Literal["N5", "N4", "N3", "N2", "N1"]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    level: Optional[Level] = None
    level_mode: Literal["exact", "at_or_below"] = "exact"
    top_k: int = Field(default=5, ge=1, le=20)


class Hit(BaseModel):
    ref: str
    chunk_id: str
    jlpt_level: str
    pattern: Optional[str] = None
    score: float
    text: str
    source_url: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    level_filter: Optional[list[str]]
    embedding_model: str
    hits: list[Hit]
    timing_ms: dict[str, int]