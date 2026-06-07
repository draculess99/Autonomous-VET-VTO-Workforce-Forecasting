from crewai import Crew

# Agents
from agents.forecast_agent import forecast_agent
from agents.cost_agent import cost_agent
from agents.staffing_agent import staffing_agent
from agents.executive_agent import executive_agent
from agents.risk_agent import risk_agent

# Tasks
from tasks.forecast_task import build_forecast_task
from tasks.cost_task import build_cost_task
from tasks.staffing_task import build_staffing_task
from tasks.executive_task import build_executive_task
from tasks.risk_task import build_risk_task

from graph.operational_graph import run_operational_graph

from graph.operational_state import OperationalState
from graph.autonomous_supervisor import run_autonomous_supervisor

# ==========================================
# Memory
# ==========================================

from memory.memory_manager import (
    add_operational_memory,
    retrieve_relevant_memories
)

# Shared Operational State
from graph.operational_state import OperationalState


def run_operational_crew(
    result_df,
    stress_band,
    total_cost,
    peak_week,
    confidence_score,
    primary_risk_display,
    vet_weeks,
    vto_weeks
):
    
    # -----------------------------
    # Retrieve Memory FIRST
    # -----------------------------

    if vet_weeks > vto_weeks:
        memory_type = "VET"
    else:
        memory_type = "VTO"

    # ---------------------------------------------------
    # Retrieve historical operational memory
    # ---------------------------------------------------

    past_memories = retrieve_relevant_memories(
        action_type=memory_type
    )

    # ==========================================
    # Build memory context
    # ==========================================
    memory_context = "\n".join([
        f"- {m['summary']}"
        for m in past_memories
    ])

    # -----------------------------------
    # Create Shared Operational State
    # -----------------------------------
    
    state = OperationalState(
        peak_week=peak_week,
        total_cost=total_cost,
        stress_band=stress_band,
        confidence_score=confidence_score,
        primary_risk_display=primary_risk_display,
        vet_weeks=vet_weeks,
        vto_weeks=vto_weeks,
        memory_context=memory_context
    )

 
    # -----------------------------
    # Build Crew
    # -----------------------------

    # crew = Crew(
    #     agents=[
    #         forecast_agent,
    #         cost_agent,
    #         staffing_agent,
    #         executive_agent
    #     ],

    #     tasks=[
    #         forecast_task,
    #         cost_task,
    #         staffing_task,
    #         executive_task
    #     ],

    #     verbose=True
    # )


    # # -----------------------------
    # # Execute Node Workflow
    # # -----------------------------

    # from nodes.forecast_node import run_forecast_node
    # from nodes.staffing_node import run_staffing_node
    # from nodes.cost_node import run_cost_node
    # from nodes.executive_node import run_executive_node
    
    # state = run_forecast_node(state)
    # state = run_staffing_node(state)
    # state = run_cost_node(state)
    # state = run_executive_node(state)

    # -----------------------------
    # Execute LangGraph Workflow
    # -----------------------------

    # Execute LangGraph workflow
    state = run_operational_graph(state)

    # Convert LangGraph dict-like state back to OperationalState
    if isinstance(state, dict):
        state = OperationalState(**state)

    # Execute autonomous supervisor layer
    state = run_autonomous_supervisor(state)

    # LangGraph may return a dict-like state.
    # Convert it back to OperationalState so the rest of this file
    # can continue using state.executive_summary.
    if isinstance(state, dict):
        state = OperationalState(**state)

    # ---------------------------------------------------
    # Persist operational memory
    # ---------------------------------------------------

    add_operational_memory(
        action_type=memory_type,
        stress_level=stress_band,
        confidence=confidence_score,
        summary=state.executive_summary
    )

    # ---------------------------------------------------
    # Return final executive summary
    # ---------------------------------------------------

    return {
        "summary": state.executive_summary,
        "autonomous_summary": state.autonomous_summary,
        "final_recommendation": state.final_recommendation,
        "guardrail_status": state.guardrail_status,
        "risk_level": state.risk_level,
        "trace": state.trace,
        "state": state,
    }