from pydantic import BaseModel, Field
from typing import List

class UserStory(BaseModel):
    title: str = Field(description="A concise title for the user story")
    user_type: str = Field(description="The 'As a [user]' part of the story")
    goal: str = Field(description="The 'I want [goal]' part of the story")
    benefit: str = Field(description="The 'So that [benefit]' part of the story")
    acceptance_criteria: List[str] = Field(description="List of acceptance criteria items")

class StoryGenerationResult(BaseModel):
    stories: List[UserStory] = Field(description="List of generated user stories, strictly between 10 and 50 items.")
