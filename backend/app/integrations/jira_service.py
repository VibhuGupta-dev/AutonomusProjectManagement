import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class JiraCredentials(BaseModel):
    base_url: str
    email: Optional[str] = None
    api_token: Optional[str] = None
    oauth_token: Optional[str] = None
    story_points_field_id: Optional[str] = None # Commonly e.g., "customfield_10016"

class JiraStory(BaseModel):
    project_key: str
    summary: str
    description: str
    acceptance_criteria: List[str]
    priority: str # Critical, High, Medium, Low
    story_points: Optional[int] = None

class JiraService:
    """Service to interact with Jira Cloud REST APIs (v2 and Agile 1.0)"""
    def __init__(self, credentials: JiraCredentials):
        self.base_url = credentials.base_url.rstrip('/')
        self.story_points_field = credentials.story_points_field_id
        
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if credentials.oauth_token:
            self.headers["Authorization"] = f"Bearer {credentials.oauth_token}"
            self.auth = None
        elif credentials.email and credentials.api_token:
            self.auth = (credentials.email, credentials.api_token)
        else:
            raise ValueError("Must provide either oauth_token OR email+api_token")

    def _map_priority(self, internal_priority: str) -> str:
        """Map internal priorities to standard Jira priorities."""
        mapping = {
            "Critical": "Highest",
            "High": "High",
            "Medium": "Medium",
            "Low": "Low"
        }
        return mapping.get(internal_priority, "Medium")

    def _format_description(self, description: str, criteria: List[str]) -> str:
        """Append acceptance criteria to description in Jira wiki markup format."""
        formatted = f"{description}\n\n*Acceptance Criteria:*\n"
        for idx, criterion in enumerate(criteria, 1):
            formatted += f"* {criterion}\n"
        return formatted

    async def create_story(self, story: JiraStory) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/2/issue"
        
        full_desc = self._format_description(story.description, story.acceptance_criteria)
        jira_priority = self._map_priority(story.priority)
        
        payload = {
            "fields": {
                "project": {"key": story.project_key},
                "summary": story.summary,
                "description": full_desc,
                "issuetype": {"name": "Story"},
                "priority": {"name": jira_priority}
            }
        }
        
        # Handle Story Points
        if story.story_points is not None:
            if self.story_points_field:
                payload["fields"][self.story_points_field] = story.story_points
            else:
                # Fallback if custom field ID is not known
                payload["fields"]["description"] = f"*Story Points:* {story.story_points}\n\n" + full_desc
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers, auth=self.auth)
            
            # Fallback to "Task" if "Story" is not a valid issue type
            if response.status_code == 400 and "issuetype" in response.text:
                payload["fields"]["issuetype"] = {"name": "Task"}
                response = await client.post(url, json=payload, headers=self.headers, auth=self.auth)

            if response.status_code >= 400:
                raise Exception(f"Jira API Error (Status {response.status_code}): {response.text}")
            return response.json()

    async def update_story(self, issue_key: str, story: JiraStory) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        
        full_desc = self._format_description(story.description, story.acceptance_criteria)
        jira_priority = self._map_priority(story.priority)
        
        payload = {
            "fields": {
                "summary": story.summary,
                "description": full_desc,
                "priority": {"name": jira_priority}
            }
        }
        
        if story.story_points is not None:
            if self.story_points_field:
                payload["fields"][self.story_points_field] = story.story_points
            else:
                payload["fields"]["description"] = f"*Story Points:* {story.story_points}\n\n" + full_desc
             
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=self.headers, auth=self.auth)
            if response.status_code >= 400:
                raise Exception(f"Jira API Error (Status {response.status_code}): {response.text}")
            return {"status": "success", "issue_key": issue_key}
            
    # --- Agile Sprint Syncing Methods ---

    async def get_or_create_sprint(self, board_id: int, sprint_name: str, goal: str = "") -> int:
        """Finds a sprint by name on a board, or creates it if it doesn't exist."""
        # 1. Search for existing
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, auth=self.auth)
            if response.status_code == 200:
                sprints = response.json().get("values", [])
                for sprint in sprints:
                    if sprint["name"].lower() == sprint_name.lower():
                        return sprint["id"]
        
        # 2. Create if not found
        create_url = f"{self.base_url}/rest/agile/1.0/sprint"
        payload = {
            "name": sprint_name,
            "originBoardId": board_id,
            "goal": goal
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(create_url, json=payload, headers=self.headers, auth=self.auth)
            if response.status_code >= 400:
                raise Exception(f"Jira API Error (Sprint Creation Status {response.status_code}): {response.text}")
            return response.json().get("id")

    async def assign_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]):
        """Moves an array of Jira issue keys into a specific Sprint."""
        if not issue_keys:
            return {"status": "no issues to assign"}
            
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        payload = {"issues": issue_keys}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers, auth=self.auth)
            if response.status_code >= 400:
                raise Exception(f"Jira API Error (Sprint Assign Status {response.status_code}): {response.text}")
            return {"status": "success", "sprint_id": sprint_id, "issues_assigned": len(issue_keys)}

    async def get_projects(self) -> List[Dict[str, Any]]:
        """Fetch all accessible projects"""
        url = f"{self.base_url}/rest/api/2/project"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, auth=self.auth)
            if response.status_code == 200:
                return [{"id": p["id"], "key": p["key"], "name": p["name"]} for p in response.json()]
            response.raise_for_status()
            return []

    async def get_boards(self) -> List[Dict[str, Any]]:
        """Fetch all agile boards"""
        url = f"{self.base_url}/rest/agile/1.0/board"
        boards = []
        async with httpx.AsyncClient() as client:
            # Only fetching first 50 boards for simplicity, Jira paginates
            response = await client.get(f"{url}?maxResults=50", headers=self.headers, auth=self.auth)
            if response.status_code == 200:
                data = response.json().get("values", [])
                for b in data:
                    boards.append({"id": b["id"], "name": b["name"], "type": b["type"]})
            else:
                response.raise_for_status()
        return boards
