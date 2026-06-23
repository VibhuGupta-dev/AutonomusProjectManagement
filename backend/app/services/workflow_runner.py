import logging
import traceback
import json
import os
import google.generativeai as genai
from app.db.prisma import db

logger = logging.getLogger(__name__)

# Setup Gemini API (Make sure GEMINI_API_KEY is in .env or system env)
# We handle the configuration inside the function to ensure it uses the latest env var

def extract_text_from_file(file_path: str, mime_type: str) -> str:
    text = ""
    try:
        if file_path.endswith(".pdf") or mime_type == "application/pdf":
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif file_path.endswith(".docx") or mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        text = f"Error extracting text: {e}"
    return text

async def run_workflow_background(file_path: str, mime_type: str, project_id: str, document_id: str):
    logger.info(f"Starting Real AI Background Workflow for Document {document_id}")
    
    # 1. Mark as processing
    await db.document.update(
        where={'id': document_id},
        data={'status': 'PROCESSING'}
    )
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables!")
        
        genai.configure(api_key=api_key)

        # Extract text
        raw_text = extract_text_from_file(file_path, mime_type)
        if not raw_text.strip():
            raw_text = "No extractable text found in document."

        # Truncate to avoid Gemini token limits if it's too huge
        raw_text = raw_text[:100000] 

        prompt = f"""
You are an expert AI Product Manager. Analyze the following project requirements document and generate:
1. Business Goals (array of strings)
2. Stakeholders (array of strings)
3. Sprints (array of objects containing sprint_name and goal)
4. User Stories (array of objects containing title, description, priority [LOW, MEDIUM, HIGH, CRITICAL], points [int], and sprint_name)

Respond ONLY with valid JSON. Do not include markdown formatting like ```json.
The structure must be exactly:
{{
  "business_goals": ["...", "..."],
  "stakeholders": ["...", "..."],
  "sprints": [
    {{"sprint_name": "Sprint 1: Foundation", "goal": "..."}}
  ],
  "stories": [
    {{"title": "...", "description": "...", "priority": "HIGH", "points": 5, "sprint_name": "Sprint 1: Foundation"}}
  ]
}}

DOCUMENT:
{raw_text}
"""
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Clean response string to just parseable JSON
        json_str = response.text.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        parsed_data = json.loads(json_str)
        
        # Save Requirement Analysis
        await db.requirementanalysis.create(
            data={
                "document": {"connect": {"id": document_id}},
                "businessGoals": json.dumps(parsed_data.get("business_goals", [])),
                "stakeholders": json.dumps(parsed_data.get("stakeholders", [])),
                "rawExtracted": raw_text[:5000] # Save a snippet of the raw text
            }
        )
        
        # Save Sprints and Stories
        sprint_map = {}
        for s in parsed_data.get("sprints", []):
            db_sprint = await db.sprintplan.create(
                data={
                    "project": {"connect": {"id": project_id}},
                    "name": s.get("sprint_name", "Sprint"),
                    "goal": s.get("goal", "")
                }
            )
            sprint_map[s.get("sprint_name")] = db_sprint.id
            
        for story in parsed_data.get("stories", []):
            sprint_id = sprint_map.get(story.get("sprint_name"))
            if sprint_id:
                await db.userstory.create(
                    data={
                        "project": {"connect": {"id": project_id}},
                        "sprintPlan": {"connect": {"id": sprint_id}},
                        "title": story.get("title", "Untitled"),
                        "description": story.get("description", ""),
                        "storyPoints": story.get("points", 3),
                        "priority": story.get("priority", "MEDIUM"),
                        "status": "READY"
                    }
                )

        # 6. Mark as completed
        await db.document.update(
            where={'id': document_id},
            data={'status': 'COMPLETED'}
        )
        logger.info(f"Background Workflow Completed successfully for Document {document_id}")
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        traceback.print_exc()
        await db.document.update(
            where={'id': document_id},
            data={'status': 'ERROR'}
        )
