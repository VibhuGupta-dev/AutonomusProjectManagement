import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.agent.state import GraphState
from app.agent.schemas import RequirementAnalysisResult
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq LLM
# Ensure GROQ_API_KEY is available in your .env file
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
structured_llm = llm.with_structured_output(RequirementAnalysisResult)

prompt_template = PromptTemplate(
    template="""You are an expert AI Product Manager. Analyze the following requirement document and extract the necessary information exactly in the requested structured format.
    
    Document:
    {document}
    """,
    input_variables=["document"],
)

def analyze_requirements(state: GraphState) -> GraphState:
    logger.info("--- ANALYZING REQUIREMENTS ---")
    raw_document = state.get("raw_document", "")
    retry_count = state.get("retry_count", 0)
    
    try:
        chain = prompt_template | structured_llm
        result: RequirementAnalysisResult = chain.invoke({"document": raw_document})
        return {"analysis_result": result, "error": None}
    except Exception as e:
        logger.error(f"Error in analyze_requirements: {e}")
        return {"error": str(e), "retry_count": retry_count + 1}

def validate_output(state: GraphState) -> GraphState:
    logger.info("--- VALIDATING OUTPUT ---")
    result = state.get("analysis_result")
    error = state.get("error")
    
    if error:
        # Pass through the error from the analyzer
        return state
        
    if not result:
        return {"error": "No result generated", "retry_count": state.get("retry_count", 0) + 1}
    
    # Validation rules
    if not result.business_goals:
        return {"error": "Validation failed: No business goals extracted.", "retry_count": state.get("retry_count", 0) + 1}
        
    if not result.functional_requirements:
         return {"error": "Validation failed: No functional requirements extracted.", "retry_count": state.get("retry_count", 0) + 1}

    # All validations passed
    return {"error": None}
