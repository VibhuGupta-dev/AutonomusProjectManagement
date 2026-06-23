import logging
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.agent.estimation.state import EstimationGraphState
from app.agent.estimation.schemas import EstimationBatchResult
from app.core.config import settings

logger = logging.getLogger(__name__)

# Using a lower temperature for consistent, analytical estimation
llm = ChatGroq(temperature=0.1, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
structured_llm = llm.with_structured_output(EstimationBatchResult)

prompt_template = PromptTemplate(
    template="""You are an Expert Agile Scrum Master and Technical Architect. Estimate the following user stories using ONLY the following Fibonacci sequence values: 1, 2, 3, 5, 8, 13, 21.

    For each story, carefully analyze and provide reasoning based on:
    1. Complexity: How difficult is the logic?
    2. Risk: Are there unknowns or potential blockers?
    3. Dependencies: Does this rely on other teams, APIs, or stories?
    4. Technical effort: How much raw coding/testing time is needed?

    User Stories to Estimate:
    {stories_json}
    """,
    input_variables=["stories_json"],
)

def estimate_stories(state: EstimationGraphState) -> EstimationGraphState:
    logger.info("--- ESTIMATING STORIES ---")
    stories = state.get("stories", [])
    retry_count = state.get("retry_count", 0)
    
    try:
        # Pass stories as formatted JSON to the LLM
        stories_str = json.dumps(stories, indent=2)
        chain = prompt_template | structured_llm
        result: EstimationBatchResult = chain.invoke({"stories_json": stories_str})
        
        return {"estimations": result.estimations, "error": None}
    except Exception as e:
        logger.error(f"Error estimating stories: {e}")
        return {"error": str(e), "retry_count": retry_count + 1}

def validate_estimations(state: EstimationGraphState) -> EstimationGraphState:
    logger.info("--- VALIDATING ESTIMATIONS ---")
    estimations = state.get("estimations", [])
    stories = state.get("stories", [])
    error = state.get("error")
    
    if error:
        return state
        
    if not estimations:
        return {"error": "No estimations generated", "retry_count": state.get("retry_count", 0) + 1}
        
    # Validation 1: Count mismatch
    if len(estimations) != len(stories):
         return {"error": f"Mismatch: Provided {len(stories)} stories, but got {len(estimations)} estimations.", "retry_count": state.get("retry_count", 0) + 1}
         
    # Validation 2: Ensure strictly valid Fibonacci points (safeguard against LLM hallucination)
    valid_fib = {1, 2, 3, 5, 8, 13, 21}
    for est in estimations:
        if est.points not in valid_fib:
             return {"error": f"Invalid story point {est.points} for story {est.story_id}. Must be from {valid_fib}.", "retry_count": state.get("retry_count", 0) + 1}
        
    return {"error": None}
