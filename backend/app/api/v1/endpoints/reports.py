import os
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.services.report_generator import ReportData, generate_pdf_report, generate_docx_report
from app.core.config import settings

router = APIRouter()

# Ensure reports directory exists
REPORTS_DIR = os.path.join(settings.UPLOAD_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def cleanup_file(filepath: str):
    """Background task to remove the report after it has been downloaded."""
    if os.path.exists(filepath):
        os.remove(filepath)

@router.post("/generate/pdf")
async def create_pdf_report(data: ReportData, background_tasks: BackgroundTasks):
    try:
        filename = f"report_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        generate_pdf_report(data, filepath)
        
        # Optionally schedule cleanup after 5 minutes, or just clean immediately after send
        # FileResponse takes a background task
        return FileResponse(
            path=filepath, 
            filename=f"{data.project_name.replace(' ', '_')}_Report.pdf",
            media_type="application/pdf",
            background=BackgroundTasks([cleanup_file, filepath]) # Note: FileResponse accepts background tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.post("/generate/docx")
async def create_docx_report(data: ReportData):
    try:
        filename = f"report_{uuid.uuid4().hex}.docx"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        generate_docx_report(data, filepath)
        
        return FileResponse(
            path=filepath, 
            filename=f"{data.project_name.replace(' ', '_')}_Report.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            background=BackgroundTasks([cleanup_file, filepath])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")
