from crewai import Task
from agents.forecast_agent import forecast_agent


def build_forecast_task(
    peak_week,
    total_cost,
    stress_band,
    confidence,
    primary_risk_display
):

    return Task(

        description=f"""
        Analyze the warehouse demand forecast
        and operational workload trends.

        Forecast Details:
        - Peak Week: {peak_week}
        - Total Labor Cost: ${total_cost:,.0f}
        - Stress Level: {stress_band}
        - Operational Confidence Score: {confidence:.0f}%
        - Primary Operational Risk Driver:
          {primary_risk_display}

        Analyze:
        - workload direction
        - demand patterns
        - operational forecasting trends
        - workload stability
        - operational readiness

        Provide concise executive observations.
        """,

        expected_output="""
        Executive warehouse forecasting summary
        in concise operational business language.
        """,

        agent=forecast_agent
    )