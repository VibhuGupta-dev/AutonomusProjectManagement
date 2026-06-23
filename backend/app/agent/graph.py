from langgraph.graph import StateGraph, END
from app.agent.state import GraphState
from app.agent.nodes import analyze_requirements, validate_output

def should_retry(state: GraphState) -> str:
    """Determine whether to retry or end based on error and retry count."""
    error = state.get("error")
    retry_count = state.get("retry_count", 0)
    
    if error and retry_count < 3:
        return "retry"
    elif error:
        return "end" # Give up after 3 retries
    else:
        return "end" # Success

# Define the workflow
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("analyzer", analyze_requirements)
workflow.add_node("validator", validate_output)

# Add edges
workflow.set_entry_point("analyzer")
workflow.add_edge("analyzer", "validator")

# Conditional edge based on validation
workflow.add_conditional_edges(
    "validator",
    should_retry,
    {
        "retry": "analyzer",
        "end": END
    }
)

# Compile the graph
requirement_analyzer_app = workflow.compile()
