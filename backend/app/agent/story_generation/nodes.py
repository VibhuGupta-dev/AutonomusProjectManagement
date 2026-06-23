import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.agent.story_generation.state import StoryGraphState
from app.agent.story_generation.schemas import StoryGenerationResult
from app.core.config import settings

logger = logging.getLogger(__name__)

# Using a slightly higher temperature for creative story generation
llm = ChatGroq(temperature=0.2, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
structured_llm = llm.with_structured_output(StoryGenerationResult)

prompt_template = PromptTemplate(
    template="""You are an Expert Agile Product Manager. Based on the following requirements analysis, generate between 10 and 50 comprehensive Agile user stories.
    
    Rules:
    - Follow the INVEST principle (Independent, Negotiable, Valuable, Estimable, Small, Testable).
    - Ensure no duplicates.
    - Focus heavily on business value and user needs.
    - Generate them as distinct features that address the functional and non-functional requirements.
    
    Requirements Analysis:
    {analysis}
    """,
    input_variables=["analysis"],
)

def generate_stories(state: StoryGraphState) -> StoryGraphState:
    logger.info("--- GENERATING USER STORIES ---")
    analysis = state.get("analysis_result")
    retry_count = state.get("retry_count", 0)
    
    try:
        chain = prompt_template | structured_llm
        # Serialize the analysis result to a string representation
        analysis_str = analysis.model_dump_json(indent=2) if analysis else "{}"
        result: StoryGenerationResult = chain.invoke({"analysis": analysis_str})
        return {"generation_result": result, "error": None}
    except Exception as e:
        logger.error(f"Error generating stories: {e}")
        return {"error": str(e), "retry_count": retry_count + 1}

def validate_stories(state: StoryGraphState) -> StoryGraphState:
    logger.info("--- VALIDATING USER STORIES ---")
    result = state.get("generation_result")
    error = state.get("error")
    
    if error:
        return state
        
    if not result or not result.stories:
        return {"error": "No stories generated", "retry_count": state.get("retry_count", 0) + 1}
        
    story_count = len(result.stories)
    if story_count < 10:
        return {"error": f"Generated only {story_count} stories, expected at least 10.", "retry_count": state.get("retry_count", 0) + 1}
        
    if story_count > 50:
         return {"error": f"Generated too many stories: {story_count}, maximum is 50.", "retry_count": state.get("retry_count", 0) + 1}
         
    # Check for duplicates or missing fields
    seen_titles = set()
    for story in result.stories:
        if story.title in seen_titles:
             return {"error": f"Duplicate story title found: {story.title}", "retry_count": state.get("retry_count", 0) + 1}
        seen_titles.add(story.title)
        
    return {"error": None}
