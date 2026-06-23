from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.prisma import db
from app.core.security import get_current_user

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.post("/")
async def create_project(data: ProjectCreate, user_id: str = Depends(get_current_user)):
    # Upsert user to ensure they exist in DB
    user = await db.user.find_unique(where={'id': user_id})
    if not user:
        # Create dummy email since Clerk handles actual auth
        await db.user.create(data={
            'id': user_id,
            'email': f"{user_id}@clerk.local",
            'name': "Dashboard User"
        })
        
    project = await db.project.create(
        data={
            'name': data.name,
            'description': data.description,
            'userId': user_id
        }
    )
    return project

@router.get("/")
async def get_projects(user_id: str = Depends(get_current_user)):
    projects = await db.project.find_many(
        where={'userId': user_id},
        order={'createdAt': 'desc'}
    )
    return projects

@router.get("/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.project.find_unique(
        where={'id': project_id},
        include={
            'documents': True,
            'sprints': {
                'include': {
                    'stories': True
                }
            },
            'reports': True
        }
    )
    if not project or project.userId != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
