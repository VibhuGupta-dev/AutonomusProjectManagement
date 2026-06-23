from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.integrations.jira_service import JiraService, JiraCredentials, JiraStory
from pydantic import BaseModel

router = APIRouter()

# In production, credentials would be fetched securely from DB/Environment based on current user
class JiraSyncRequest(BaseModel):
    credentials: JiraCredentials
    stories: List[JiraStory]

@router.post("/sync/stories")
async def sync_stories_to_jira(request: JiraSyncRequest):
    """Creates multiple stories in Jira"""
    try:
        service = JiraService(request.credentials)
        results = []
        for story in request.stories:
            response = await service.create_story(story)
            results.append({
                "internal_title": story.summary,
                "jira_key": response.get("key"),
                "jira_id": response.get("id")
            })
        return {"status": "success", "synced_stories": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Jira sync failed: {str(e)}")

class SprintSyncRequest(BaseModel):
    credentials: JiraCredentials
    board_id: int
    sprint_name: str
    sprint_goal: str
    issue_keys: List[str]

@router.post("/sync/sprint")
async def sync_sprint_to_jira(request: SprintSyncRequest):
    """Creates/Finds a sprint and assigns issues to it"""
    try:
        service = JiraService(request.credentials)
        sprint_id = await service.get_or_create_sprint(
            board_id=request.board_id,
            sprint_name=request.sprint_name,
            goal=request.sprint_goal
        )
        
        result = await service.assign_issues_to_sprint(sprint_id, request.issue_keys)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint sync failed: {str(e)}")

@router.post("/boards")
async def get_jira_boards(credentials: JiraCredentials):
    try:
        service = JiraService(credentials)
        boards = await service.get_boards()
        return {"status": "success", "boards": boards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch boards: {str(e)}")

@router.post("/projects")
async def get_jira_projects(credentials: JiraCredentials):
    try:
        service = JiraService(credentials)
        projects = await service.get_projects()
        return {"status": "success", "projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")
