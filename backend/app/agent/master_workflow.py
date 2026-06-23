import logging
import os
import uuid
from langgraph.graph import StateGraph, END
from app.agent.master_state import MasterState

# Import internal services and sub-graphs
from app.services.extraction import extract_text_from_file
from app.agent.graph import requirement_analyzer_app
from app.agent.story_generation.graph import story_generator_app
from app.agent.estimation.graph import estimation_app
from app.agent.prioritization.graph import prioritization_app
from app.agent.sprint_planning.graph import sprint_planner_app
from app.integrations.jira_service import JiraService, JiraCredentials, JiraStory
from app.services.report_generator import ReportData, generate_pdf_report, generate_docx_report
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- Node Definitions ---

def node_extract(state: MasterState):
    logger.info("--- [MASTER] EXTRACTING TEXT ---")
    try:
        text = extract_text_from_file(state["file_path"], state["mime_type"])
        return {"raw_document": text, "error": None}
    except Exception as e:
        return {"error": str(e), "failed_step": "extract"}

def node_analyze(state: MasterState):
    logger.info("--- [MASTER] ANALYZING REQUIREMENTS ---")
    try:
        result = requirement_analyzer_app.invoke({"raw_document": state["raw_document"], "retry_count": 0})
        if result.get("error"):
            return {"error": result["error"], "failed_step": "analyze"}
        return {"analysis_result": result["analysis_result"].model_dump(), "error": None}
    except Exception as e:
        return {"error": str(e), "failed_step": "analyze"}

def node_story_gen(state: MasterState):
    logger.info("--- [MASTER] GENERATING STORIES ---")
    try:
        # Pydantic models need to be reconstructed or passed directly.
        # Since state handles dicts well, we pass it back via the schema if needed.
        # Our subgraphs can accept raw dicts if prompt templates just str() them.
        from app.agent.schemas import RequirementAnalysisResult
        analysis_obj = RequirementAnalysisResult(**state["analysis_result"])
        
        result = story_generator_app.invoke({"analysis_result": analysis_obj, "retry_count": 0})
        if result.get("error"):
            return {"error": result["error"], "failed_step": "story_gen"}
            
        stories = [s.model_dump() for s in result["generation_result"].stories]
        return {"stories": stories, "error": None}
    except Exception as e:
        return {"error": str(e), "failed_step": "story_gen"}

def node_estimate(state: MasterState):
    logger.info("--- [MASTER] ESTIMATING STORY POINTS ---")
    try:
        result = estimation_app.invoke({"stories": state["stories"], "retry_count": 0})
        if result.get("error"):
            return {"error": result["error"], "failed_step": "estimate"}
            
        estimations = result["estimations"]
        stories_w_est = []
        for story in state["stories"]:
            story_dict = story.copy()
            est_match = next((e for e in estimations if e.story_id == story["title"]), None)
            story_dict["points"] = est_match.points if est_match else 5
            stories_w_est.append(story_dict)
            
        return {"stories_with_estimations": stories_w_est, "error": None}
    except Exception as e:
        return {"error": str(e), "failed_step": "estimate"}

def node_prioritize(state: MasterState):
    logger.info("--- [MASTER] PRIORITIZING BACKLOG ---")
    try:
        result = prioritization_app.invoke({"stories_with_estimations": state["stories_with_estimations"], "retry_count": 0})
        if result.get("error"):
            return {"error": result["error"], "failed_step": "prioritize"}
            
        backlog = result["ranked_backlog"]
        final_stories = []
        for ranked in backlog.ranked_stories:
            orig = next((s for s in state["stories_with_estimations"] if s["title"] == ranked.story_id), None)
            if orig:
                orig["priority"] = ranked.priority
                final_stories.append(orig)
        return {"ranked_backlog": final_stories, "error": None}
    except Exception as e:
        return {"error": str(e), "failed_step": "prioritize"}

def node_sprint_plan(state: MasterState):
    logger.info("--- [MASTER] PLANNING SPRINTS ---")
    try:
        result = sprint_planner_app.invoke({"ranked_backlog": state["ranked_backlog"], "retry_count": 0})
        if result.get("error"):
            return {"error": result["error"], "failed_step": "sprint_plan"}
            
        return {"sprint_plan": result["sprint_plan"].model_dump(), "error": None}
    except Exception as e:
        return {"error": str(e), "failed_step": "sprint_plan"}

async def node_jira_sync(state: MasterState):
    logger.info("--- [MASTER] SYNCING TO JIRA ---")
    creds_dict = state.get("jira_credentials")
    if not creds_dict:
        logger.info("No Jira credentials provided, skipping sync.")
        return {"stories_with_jira": state.get("ranked_backlog", []), "error": None}
        
    try:
        creds = JiraCredentials(**creds_dict)
        service = JiraService(creds)
        updated_stories = []
        for story in state["ranked_backlog"]:
            j_story = JiraStory(
                project_key=creds_dict.get("project_key", "PROJ"),
                summary=story["title"],
                description=f"As a {story.get('user_type')} I want {story.get('goal')} so that {story.get('benefit')}",
                acceptance_criteria=story.get("acceptance_criteria", []),
                priority=story.get("priority", "Medium"),
                story_points=story.get("points")
            )
            resp = await service.create_story(j_story)
            story_copy = story.copy()
            story_copy["jira_url"] = f"{creds.base_url}/browse/{resp.get('key')}"
            updated_stories.append(story_copy)
            
        return {"stories_with_jira": updated_stories, "error": None}
    except Exception as e:
        return {"error": str(e), "failed_step": "jira_sync"}

def dummy_fork(state: MasterState):
    # This node is just a router to trigger parallel execution for reports
    logger.info("--- [MASTER] FAN-OUT TO PARALLEL REPORT GENERATION ---")
    return state

def node_generate_pdf(state: MasterState):
    logger.info("--- [MASTER] GENERATING PDF ---")
    try:
        # Build ReportData
        data = ReportData(
            project_name=state.get("project_name", "AI PM Project"),
            requirements_summary=state.get("raw_document", "")[:500] + "... (Truncated)",
            stories=state.get("stories_with_jira", []),
            sprint_plan=state.get("sprint_plan", {}).get("sprints", [])
        )
        reports_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        pdf_path = os.path.join(reports_dir, f"report_{uuid.uuid4().hex}.pdf")
        
        generate_pdf_report(data, pdf_path)
        return {"pdf_report_path": pdf_path}
    except Exception as e:
        logger.error(f"PDF Gen Error: {e}")
        return {"pdf_report_path": "error"}

def node_generate_docx(state: MasterState):
    logger.info("--- [MASTER] GENERATING DOCX ---")
    try:
        data = ReportData(
            project_name=state.get("project_name", "AI PM Project"),
            requirements_summary=state.get("raw_document", "")[:500] + "... (Truncated)",
            stories=state.get("stories_with_jira", []),
            sprint_plan=state.get("sprint_plan", {}).get("sprints", [])
        )
        reports_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        docx_path = os.path.join(reports_dir, f"report_{uuid.uuid4().hex}.docx")
        
        generate_docx_report(data, docx_path)
        return {"docx_report_path": docx_path}
    except Exception as e:
        logger.error(f"DOCX Gen Error: {e}")
        return {"docx_report_path": "error"}

def error_handler(state: MasterState):
    logger.error(f"--- [MASTER] PIPELINE FAILED AT: {state.get('failed_step')} ---")
    logger.error(f"Error Details: {state.get('error')}")
    return state

# --- Graph Definition ---

def check_error(state: MasterState) -> str:
    """Routing function to catch errors early"""
    return "error_handler" if state.get("error") else "next"

workflow = StateGraph(MasterState)

# Add all nodes
workflow.add_node("extract", node_extract)
workflow.add_node("analyze", node_analyze)
workflow.add_node("story_gen", node_story_gen)
workflow.add_node("estimate", node_estimate)
workflow.add_node("prioritize", node_prioritize)
workflow.add_node("sprint_plan", node_sprint_plan)
workflow.add_node("jira_sync", node_jira_sync)

# Parallel execution setup
workflow.add_node("parallel_fork", dummy_fork)
workflow.add_node("gen_pdf", node_generate_pdf)
workflow.add_node("gen_docx", node_generate_docx)
workflow.add_node("error_handler", error_handler)

# Edge wiring with error recovery checks at each step
workflow.set_entry_point("extract")
workflow.add_conditional_edges("extract", check_error, {"next": "analyze", "error_handler": "error_handler"})
workflow.add_conditional_edges("analyze", check_error, {"next": "story_gen", "error_handler": "error_handler"})
workflow.add_conditional_edges("story_gen", check_error, {"next": "estimate", "error_handler": "error_handler"})
workflow.add_conditional_edges("estimate", check_error, {"next": "prioritize", "error_handler": "error_handler"})
workflow.add_conditional_edges("prioritize", check_error, {"next": "sprint_plan", "error_handler": "error_handler"})
workflow.add_conditional_edges("sprint_plan", check_error, {"next": "jira_sync", "error_handler": "error_handler"})

# After Jira sync, conditionally go to the parallel fork
workflow.add_conditional_edges("jira_sync", check_error, {"next": "parallel_fork", "error_handler": "error_handler"})

# FAN-OUT: Trigger PDF and DOCX concurrently
workflow.add_edge("parallel_fork", "gen_pdf")
workflow.add_edge("parallel_fork", "gen_docx")

# FAN-IN & END
workflow.add_edge("gen_pdf", END)
workflow.add_edge("gen_docx", END)
workflow.add_edge("error_handler", END)

master_agent_app = workflow.compile()
