from typing import TypedDict, Optional
from app.agent.schemas import RequirementAnalysisResult
from app.agent.story_generation.schemas import StoryGenerationResult

class StoryGraphState(TypedDict):
    analysis_result: RequirementAnalysisResult
    generation_result: Optional[StoryGenerationResult]
    error: Optional[str]
    retry_count: int
