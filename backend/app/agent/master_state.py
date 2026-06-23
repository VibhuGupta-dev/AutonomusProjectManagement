from typing import TypedDict, Optional, List, Dict, Any

class MasterState(TypedDict):
    # Inputs
    project_name: str
    file_path: str
    mime_type: str
    jira_credentials: Optional[Dict[str, Any]]
    
    # Accumulated State (from sub-agents)
    raw_document: str
    analysis_result: Optional[Dict[str, Any]]
    stories: List[Dict[str, Any]]
    stories_with_estimations: List[Dict[str, Any]]
    ranked_backlog: List[Dict[str, Any]]
    sprint_plan: Optional[Dict[str, Any]]
    stories_with_jira: List[Dict[str, Any]]
    
    # Final Outputs
    pdf_report_path: Optional[str]
    docx_report_path: Optional[str]
    
    # Error Handling & Tracking
    error: Optional[str]
    failed_step: Optional[str]
