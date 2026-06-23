from langgraph.graph import StateGraph, END
from app.agent.story_generation.state import StoryGraphState
from app.agent.story_generation.nodes import generate_stories, validate_stories

def should_retry(state: StoryGraphState) -> str:
    """Determine whether to retry generation or end the workflow based on error status."""
    error = state.get("error")
    retry_count = state.get("retry_count", 0)
    
    if error and retry_count < 3:
        return "retry"
    elif error:
        return "end" # Max retries reached
    else:
        return "end" # Success

workflow = StateGraph(StoryGraphState)

# Add nodes
workflow.add_node("generator", generate_stories)
workflow.add_node("validator", validate_stories)

# Build edges
workflow.set_entry_point("generator")
workflow.add_edge("generator", "validator")

workflow.add_conditional_edges(
    "validator",
    should_retry,
    {
        "retry": "generator",
        "end": END
    }
)

# Compile graph
story_generator_app = workflow.compile()
