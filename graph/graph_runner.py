# graph_runner.py

# graph/graph_runner.py

from graph.operational_state import OperationalState

from nodes.forecast_node import run_forecast_node
from nodes.staffing_node import run_staffing_node
from nodes.cost_node import run_cost_node
from nodes.executive_node import run_executive_node


def run_operational_workflow(input_data=None):
    """
    Manual orchestration runner for the VET/VTO workflow.

    This proves that the node/state pipeline works before converting
    the workflow into a full LangGraph StateGraph.
    """

    # Create initial state
    state = OperationalState()

    # Store original input if your state supports it
    if input_data is not None:
        state.input_data = input_data

    # Run nodes in sequence
    state = run_forecast_node(state)
    state = run_staffing_node(state)
    state = run_cost_node(state)
    state = run_executive_node(state)

    return state


if __name__ == "__main__":
    final_state = run_operational_workflow()

    print("\n==============================")
    print("FINAL EXECUTIVE SUMMARY")
    print("==============================")
    print(final_state.executive_summary)