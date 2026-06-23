from langgraph.graph import StateGraph, END
from app.agent.sprint_planning.state import SprintPlanningGraphState
from app.agent.sprint_planning.nodes import plan_sprints, validate_sprint_plan

def should_retry(state: SprintPlanningGraphState) -> str:
    """Retry sprint generation if capacity limits or missing stories cause validation errors."""
    error = state.get("error")
    retry_count = state.get("retry_count", 0)
    
    if error and retry_count < 3:
        return "retry"
    elif error:
        return "end" # Max retries reached
    else:
        return "end" # Success

workflow = StateGraph(SprintPlanningGraphState)

# Add nodes
workflow.add_node("planner", plan_sprints)
workflow.add_node("validator", validate_sprint_plan)

# Build edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "validator")

workflow.add_conditional_edges(
    "validator",
    should_retry,
    {
        "retry": "planner",
        "end": END
    }
)

# Compile graph
sprint_planner_app = workflow.compile()
