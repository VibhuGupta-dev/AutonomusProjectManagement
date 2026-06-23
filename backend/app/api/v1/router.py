from fastapi import APIRouter
from app.api.v1.endpoints import documents
from app.api.v1.endpoints import jira
from app.api.v1.endpoints import reports
from app.api.v1.endpoints import projects

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(jira.router, prefix="/jira", tags=["jira"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
