from pydantic import BaseModel, Field
from typing import List, Literal

PriorityLevel = Literal["Critical", "High", "Medium", "Low"]

class PrioritizedStory(BaseModel):
    story_id: str = Field(description="The unique title or ID of the story")
    priority: PriorityLevel = Field(description="The assigned priority level (Critical, High, Medium, Low)")
    reasoning: str = Field(description="Reasoning based on Business Value, Risk, Dependencies, and MVP Importance")

class RankedBacklog(BaseModel):
    ranked_stories: List[PrioritizedStory] = Field(description="List of stories ranked by priority (Critical first, then High, etc.)")
