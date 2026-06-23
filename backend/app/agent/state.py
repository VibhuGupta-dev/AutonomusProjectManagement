from typing import TypedDict, Optional
from app.agent.schemas import RequirementAnalysisResult

class GraphState(TypedDict):
    raw_document: str
    analysis_result: Optional[RequirementAnalysisResult]
    error: Optional[str]
    retry_count: int
