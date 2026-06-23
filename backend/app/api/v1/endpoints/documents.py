import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from app.core.config import settings
from app.db.prisma import db
from app.services.workflow_runner import run_workflow_background
from app.core.security import get_current_user

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "text/plain": ".txt"
}

@router.post("/upload")
async def upload_document(
    project_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    # 1. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # 2. Validate File Size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds limit")

    # 3. Secure Storage
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = ALLOWED_MIME_TYPES[file.content_type]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save file securely")
    finally:
        file.file.close()

    # 4. Save to Database
    try:
        doc = await db.document.create(
            data={
                "projectId": project_id,
                "fileName": file.filename or f"document_{file_id}",
                "fileUrl": file_path,
                "fileType": file.content_type,
                "status": "PENDING"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save document to database")

    # 5. Trigger AI Workflow in Background
    background_tasks.add_task(
        run_workflow_background,
        file_path=file_path,
        mime_type=file.content_type,
        project_id=project_id,
        document_id=doc.id
    )

    return {
        "message": "File uploaded successfully. Processing started.",
        "document_id": doc.id,
        "status": "PENDING"
    }
