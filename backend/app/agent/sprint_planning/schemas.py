from pydantic import BaseModel, Field
from typing import List

class Sprint(BaseModel):
    sprint_name: str = Field(description="Name of the sprint, e.g., 'Sprint 1', 'Sprint 2'")
    sprint_goal: str = Field(description="The primary objective or MVP theme for this sprint")
    total_points: int = Field(description="Sum of story points in this sprint (STRICTLY <= 40)")
    story_ids: List[str] = Field(description="List of story IDs assigned to this sprint")

class SprintPlanResult(BaseModel):
    sprints: List[Sprint] = Field(description="Chronological list of planned sprints ensuring MVP items are first")
    unplanned_stories: List[str] = Field(default=[], description="Story IDs that could not fit into any sprint due to constraints")
