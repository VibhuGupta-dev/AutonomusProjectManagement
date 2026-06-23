from pydantic import BaseModel, Field
from typing import List

class RequirementAnalysisResult(BaseModel):
    business_goals: List[str] = Field(description="Key business goals extracted from the document")
    stakeholders: List[str] = Field(description="List of stakeholders involved or affected")
    functional_requirements: List[str] = Field(description="List of functional requirements")
    non_functional_requirements: List[str] = Field(description="List of non-functional requirements (e.g., performance, security)")
    assumptions: List[str] = Field(description="Any assumptions made in the document")
    risks: List[str] = Field(description="Potential risks identified")
    missing_information: List[str] = Field(description="Questions or missing information that needs clarification")
