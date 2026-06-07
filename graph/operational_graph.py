from langgraph.graph import StateGraph, END

from graph.operational_state import OperationalState
from nodes.forecast_node import run_forecast_node
from nodes.staffing_node import run_staffing_node
from nodes.cost_node import run_cost_node
from nodes.executive_node import run_executive_node
from nodes.risk_node import run_risk_node

from nodes.rag_node import run_rag_node


def build_operational_graph():
    graph = StateGraph(OperationalState)

    graph.add_node("forecast", run_forecast_node)
    graph.add_node("staffing", run_staffing_node)
    graph.add_node("risk", run_risk_node)
    graph.add_node("cost", run_cost_node)
    graph.add_node("rag", run_rag_node)
    graph.add_node("executive", run_executive_node)

    graph.set_entry_point("forecast")

    graph.add_edge("forecast", "staffing")
    graph.add_edge("staffing", "risk")
    graph.add_edge("risk", "cost")
    graph.add_edge("cost", "rag")
    graph.add_edge("rag", "executive")
    graph.add_edge("executive", END)


    return graph.compile()


def run_operational_graph(state):
    app = build_operational_graph()
    return app.invoke(state)