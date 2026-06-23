from pydantic import BaseModel, Field
from typing import List, Literal

# Allowed Fibonacci points
FibonacciPoint = Literal[1, 2, 3, 5, 8, 13, 21]

class StoryEstimation(BaseModel):
    story_id: str = Field(description="The unique title or ID of the story being estimated")
    points: FibonacciPoint = Field(description="Story points using the allowed Fibonacci sequence")
    reasoning: str = Field(description="Reasoning considering Complexity, Risk, Dependencies, and Technical effort")

class EstimationBatchResult(BaseModel):
    estimations: List[StoryEstimation] = Field(description="List of story point estimations corresponding to the input stories")
