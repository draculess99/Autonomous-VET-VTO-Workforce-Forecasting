from graph.operational_state import OperationalState


def run_autonomous_supervisor(state: OperationalState) -> OperationalState:
    """
    Autonomous supervisor for the VET/VTO operational workflow.

    This layer does not replace XGBoost, CrewAI, LangGraph, or the existing
    guardrails. It reviews the completed operational state, assigns a final
    recommendation, records guardrail status, and stores a transparent trace.
    """

    trace = []

    trace.append("Supervisor started autonomous VET/VTO workflow.")

    # -------------------------------------------------
    # Check forecast output
    # -------------------------------------------------
    if not state.forecast_summary:
        state.guardrail_status = "failed"
        state.risk_level = "high"
        state.final_recommendation = "REVIEW_REQUIRED"
        state.autonomous_summary = (
            "Autonomous supervisor stopped because no forecast summary was available."
        )
        trace.append("Supervisor stopped: missing forecast summary.")
        state.trace = trace
        return state

    trace.append("Forecast output detected from forecasting node.")

    # -------------------------------------------------
    # Check staffing output
    # -------------------------------------------------
    if not state.staffing_action and not state.workforce_recommendation:
        state.guardrail_status = "failed"
        state.risk_level = "high"
        state.final_recommendation = "REVIEW_REQUIRED"
        state.autonomous_summary = (
            "Autonomous supervisor stopped because no staffing recommendation was available."
        )
        trace.append("Supervisor stopped: missing staffing recommendation.")
        state.trace = trace
        return state

    trace.append("Staffing recommendation detected from staffing node.")

    # -------------------------------------------------
    # Select final recommendation
    # -------------------------------------------------
    if state.staffing_action:
        state.final_recommendation = state.staffing_action
    else:
        state.final_recommendation = state.workforce_recommendation

    trace.append(
        f"Supervisor selected final recommendation: {state.final_recommendation}."
    )

    # -------------------------------------------------
    # Risk handling
    # -------------------------------------------------
    if state.risk_level:
        trace.append(f"Risk level detected from risk node: {state.risk_level}.")
    elif state.staffing_risk_level:
        state.risk_level = state.staffing_risk_level
        trace.append(
            f"Risk level inherited from staffing node: {state.risk_level}."
        )
    else:
        state.risk_level = "moderate"
        trace.append(
            "Risk level was not found, so supervisor assigned default moderate risk."
        )

    # -------------------------------------------------
    # Guardrail status
    # -------------------------------------------------
    state.guardrail_status = "passed"
    trace.append("Supervisor guardrail review passed.")

    # -------------------------------------------------
    # Build autonomous summary
    # -------------------------------------------------
    state.autonomous_summary = (
        f"Autonomous supervisor recommends {state.final_recommendation}. "
        f"Forecast signal: {state.forecast_summary} "
        f"Staffing analysis: {state.staffing_summary} "
        f"Risk level: {state.risk_level}. "
        "This recommendation is decision-support only and should be reviewed "
        "by a human operations manager before staffing action is taken."
    )

    trace.append("Autonomous summary generated for human review.")
    trace.append("Supervisor completed autonomous VET/VTO workflow.")

    state.trace = trace

    return state