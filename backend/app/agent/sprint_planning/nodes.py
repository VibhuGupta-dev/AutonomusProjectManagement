import logging
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.agent.sprint_planning.state import SprintPlanningGraphState
from app.agent.sprint_planning.schemas import SprintPlanResult
from app.core.config import settings

logger = logging.getLogger(__name__)

llm = ChatGroq(temperature=0.1, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
structured_llm = llm.with_structured_output(SprintPlanResult)

prompt_template = PromptTemplate(
    template="""You are an Expert Agile Release Train Engineer. Organize the following prioritized backlog of user stories into a chronological sprint plan.
    
    CRITICAL RULES:
    1. Sprint Duration: Sprints are 2-weeks long.
    2. Capacity Limit: You have a MAXIMUM velocity of 40 story points per sprint. DO NOT exceed 40 points in any single sprint. Check your math!
    3. Dependencies: Respect logical dependencies. Foundational features must be in earlier sprints.
    4. MVP First: Critical and High priority items MUST be scheduled in Sprint 1 and Sprint 2.
    
    Output the planned sprints in chronological order (Sprint 1, Sprint 2, etc.).
    
    Prioritized Backlog:
    {backlog_json}
    """,
    input_variables=["backlog_json"],
)

def plan_sprints(state: SprintPlanningGraphState) -> SprintPlanningGraphState:
    logger.info("--- PLANNING SPRINTS ---")
    backlog = state.get("ranked_backlog", [])
    retry_count = state.get("retry_count", 0)
    
    try:
        backlog_str = json.dumps(backlog, indent=2)
        chain = prompt_template | structured_llm
        result: SprintPlanResult = chain.invoke({"backlog_json": backlog_str})
        
        return {"sprint_plan": result, "error": None}
    except Exception as e:
        logger.error(f"Error planning sprints: {e}")
        return {"error": str(e), "retry_count": retry_count + 1}

def validate_sprint_plan(state: SprintPlanningGraphState) -> SprintPlanningGraphState:
    logger.info("--- VALIDATING SPRINT PLAN ---")
    plan = state.get("sprint_plan")
    backlog = state.get("ranked_backlog", [])
    error = state.get("error")
    
    if error:
        return state
        
    if not plan or not plan.sprints:
        return {"error": "No sprints generated", "retry_count": state.get("retry_count", 0) + 1}
        
    # Validation 1: Capacity Limit Enforcer (<= 40 points)
    for sprint in plan.sprints:
        if sprint.total_points > 40:
             return {"error": f"Sprint '{sprint.sprint_name}' exceeds the 40-point capacity limit (calculated {sprint.total_points} points). Re-allocate stories.", "retry_count": state.get("retry_count", 0) + 1}
             
    # Validation 2: Ensure no stories were hallucinated and all are accounted for
    input_story_ids = {story.get("story_id") for story in backlog if story.get("story_id")}
    planned_story_ids = set()
    for sprint in plan.sprints:
        planned_story_ids.update(sprint.story_ids)
    
    planned_story_ids.update(plan.unplanned_stories)
    
    missing_stories = input_story_ids - planned_story_ids
    if missing_stories:
         return {"error": f"Missing stories from plan: {missing_stories}. All input stories must be assigned to a sprint or marked unplanned.", "retry_count": state.get("retry_count", 0) + 1}
         
    return {"error": None}
