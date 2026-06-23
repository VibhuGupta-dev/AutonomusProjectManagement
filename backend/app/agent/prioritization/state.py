from typing import TypedDict, Optional, List, Dict, Any
from app.agent.prioritization.schemas import RankedBacklog

class PrioritizationGraphState(TypedDict):
    stories_with_estimations: List[Dict[str, Any]] # Input: Stories combined with their point estimations
    ranked_backlog: Optional[RankedBacklog]        # Output: The ranked backlog
    error: Optional[str]
    retry_count: int
