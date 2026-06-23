from typing import TypedDict, Optional, List, Dict, Any
from app.agent.estimation.schemas import StoryEstimation

class EstimationGraphState(TypedDict):
    stories: List[Dict[str, Any]] # Input: List of generated user stories (as dictionaries)
    estimations: List[StoryEstimation] # Output: The estimations
    error: Optional[str]
    retry_count: int
