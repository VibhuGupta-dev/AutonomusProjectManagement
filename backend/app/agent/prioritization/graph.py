from langgraph.graph import StateGraph, END
from app.agent.prioritization.state import PrioritizationGraphState
from app.agent.prioritization.nodes import prioritize_stories, validate_prioritization

def should_retry(state: PrioritizationGraphState) -> str:
    """Determine whether to retry prioritization or end the workflow based on validation errors."""
    error = state.get("error")
    retry_count = state.get("retry_count", 0)
    
    if error and retry_count < 3:
        return "retry"
    elif error:
        return "end" # Max retries reached
    else:
        return "end" # Success

workflow = StateGraph(PrioritizationGraphState)

# Add nodes
workflow.add_node("prioritizer", prioritize_stories)
workflow.add_node("validator", validate_prioritization)

# Build edges
workflow.set_entry_point("prioritizer")
workflow.add_edge("prioritizer", "validator")

workflow.add_conditional_edges(
    "validator",
    should_retry,
    {
        "retry": "prioritizer",
        "end": END
    }
)

# Compile graph
prioritization_app = workflow.compile()
