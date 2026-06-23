from langgraph.graph import StateGraph, END
from app.agent.estimation.state import EstimationGraphState
from app.agent.estimation.nodes import estimate_stories, validate_estimations

def should_retry(state: EstimationGraphState) -> str:
    """Determine whether to retry estimation or end the workflow based on validation errors."""
    error = state.get("error")
    retry_count = state.get("retry_count", 0)
    
    if error and retry_count < 3:
        return "retry"
    elif error:
        return "end" # Max retries reached
    else:
        return "end" # Success

workflow = StateGraph(EstimationGraphState)

# Add nodes
workflow.add_node("estimator", estimate_stories)
workflow.add_node("validator", validate_estimations)

# Build edges
workflow.set_entry_point("estimator")
workflow.add_edge("estimator", "validator")

workflow.add_conditional_edges(
    "validator",
    should_retry,
    {
        "retry": "estimator",
        "end": END
    }
)

# Compile graph
estimation_app = workflow.compile()
