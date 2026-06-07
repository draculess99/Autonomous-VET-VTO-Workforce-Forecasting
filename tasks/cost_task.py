from crewai import Task
from agents.cost_agent import cost_agent


def build_cost_task(
    peak_week,
    total_cost,
    stress_band,
    confidence,
    primary_risk_display
):

    return Task(

        description=f"""
        Analyze warehouse labor costs
        and operational spending exposure.

        Forecast Details:
        - Peak Week: {peak_week}
        - Total Labor Cost: ${total_cost:,.0f}
        - Stress Level: {stress_band}
        - Operational Confidence Score: {confidence:.0f}%
        - Primary Operational Risk Driver:
          {primary_risk_display}

        Analyze:
        - overtime exposure
        - labor spending
        - staffing efficiency
        - budget concerns
        - operational cost stability

        Provide concise executive recommendations.
        """,

        expected_output="""
        Concise labor cost analysis
        in executive operational language.
        """,

        agent=cost_agent
    )