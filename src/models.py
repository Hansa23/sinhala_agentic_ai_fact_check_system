"""Data models for fact checking system."""
from typing import TypedDict, List, Optional


class FactCheckState(TypedDict):
    """State for the fact-checking workflow."""
    statement: str
    domain: str
    retrieved_docs: List[dict]
    search_results: List[dict]
    analysis: str
    verdict: str
    method_used: str
    sufficiency: Optional[str]
    search_source: Optional[str]
    cached: bool
