import logging
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.agent.prioritization.state import PrioritizationGraphState
from app.agent.prioritization.schemas import RankedBacklog
from app.core.config import settings

logger = logging.getLogger(__name__)

llm = ChatGroq(temperature=0.1, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
structured_llm = llm.with_structured_output(RankedBacklog)

prompt_template = PromptTemplate(
    template="""You are an Expert Agile Product Owner. Prioritize the following user stories (which include their complexity/effort estimations).
    
    Assign EXACTLY one of the following priorities to each story: Critical, High, Medium, Low.
    
    Your prioritization MUST be based on the following criteria:
    1. Business Value (impact on the product's success)
    2. Risk (address high-risk or unknown items early)
    3. Dependencies (foundational architecture/features must be prioritized higher)
    4. MVP Importance (must-haves vs nice-to-haves)
    
    Output the final backlog ranked in order (most critical items first).
    
    Stories to Prioritize:
    {stories_json}
    """,
    input_variables=["stories_json"],
)

def prioritize_stories(state: PrioritizationGraphState) -> PrioritizationGraphState:
    logger.info("--- PRIORITIZING STORIES ---")
    stories = state.get("stories_with_estimations", [])
    retry_count = state.get("retry_count", 0)
    
    try:
        stories_str = json.dumps(stories, indent=2)
        chain = prompt_template | structured_llm
        result: RankedBacklog = chain.invoke({"stories_json": stories_str})
        
        return {"ranked_backlog": result, "error": None}
    except Exception as e:
        logger.error(f"Error prioritizing stories: {e}")
        return {"error": str(e), "retry_count": retry_count + 1}

def validate_prioritization(state: PrioritizationGraphState) -> PrioritizationGraphState:
    logger.info("--- VALIDATING PRIORITIZATION ---")
    backlog = state.get("ranked_backlog")
    stories = state.get("stories_with_estimations", [])
    error = state.get("error")
    
    if error:
        return state
        
    if not backlog or not backlog.ranked_stories:
        return {"error": "No ranked backlog generated", "retry_count": state.get("retry_count", 0) + 1}
        
    # Validation 1: Count mismatch
    if len(backlog.ranked_stories) != len(stories):
         return {"error": f"Mismatch: Provided {len(stories)} stories, but ranked {len(backlog.ranked_stories)}.", "retry_count": state.get("retry_count", 0) + 1}
         
    # Validation 2: Ensure strictly valid priorities
    valid_priorities = {"Critical", "High", "Medium", "Low"}
    for story in backlog.ranked_stories:
        if story.priority not in valid_priorities:
             return {"error": f"Invalid priority '{story.priority}' for story {story.story_id}. Must be Critical, High, Medium, or Low.", "retry_count": state.get("retry_count", 0) + 1}
        
    return {"error": None}
