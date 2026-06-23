from typing import TypedDict, Optional, List, Dict, Any
from app.agent.sprint_planning.schemas import SprintPlanResult

class SprintPlanningGraphState(TypedDict):
    ranked_backlog: List[Dict[str, Any]] # Input: Ranked backlog with estimations and priorities
    sprint_plan: Optional[SprintPlanResult] # Output: The sprint plan grouping
    error: Optional[str]
    retry_count: int
