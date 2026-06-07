# nodes/forecast_node.py

from tasks.forecast_task import build_forecast_task


def run_forecast_node(state):
    """
    Forecast node reads the current OperationalState,
    runs the forecast task, and writes forecast intelligence
    back into the shared state object.
    """

    forecast_task = build_forecast_task(
        state.peak_week,
        state.total_cost,
        state.stress_band,
        state.confidence_score,
        state.primary_risk_display
    )

    # CrewAI Task does not use .execute() in your current setup.
    # So for now, this node records structured forecast context directly.
    state.forecast_summary = (
        f"Peak Week {state.peak_week} identified under {state.stress_band} "
        f"stress with {state.confidence_score}% operational confidence. "
        f"Primary risk driver: {state.primary_risk_display}."
    )

    state.forecast_risk_signal = state.primary_risk_display
    state.forecast_confidence = state.confidence_score

    return state