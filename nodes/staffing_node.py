from crewai import Crew
from tasks.staffing_task import build_staffing_task
from agents.staffing_agent import staffing_agent


def run_staffing_node(state):

    staffing_task = build_staffing_task(
        state.peak_week,
        state.total_cost,
        state.stress_band,
        state.confidence_score,
        state.primary_risk_display,
        state.vet_weeks,
        state.vto_weeks
    )

    staffing_crew = Crew(
        agents=[staffing_agent],
        tasks=[staffing_task],
        verbose=True
    )

    staffing_result = staffing_crew.kickoff()

    staffing_text = str(staffing_result)

    state.staffing_summary = staffing_text

    lines = staffing_text.split("\n")

    for i, line in enumerate(lines):

        if "Recommended Action:" in line and i + 1 < len(lines):
            state.staffing_action = lines[i + 1].strip()

        if "Staffing Risk Level:" in line and i + 1 < len(lines):
            state.staffing_risk_level = lines[i + 1].strip()

        if "Operational Concern:" in line and i + 1 < len(lines):
            state.operational_concern = lines[i + 1].strip()

        if "Operational Reason:" in line and i + 1 < len(lines):
            state.operational_reason = lines[i + 1].strip()

        if "Workforce Recommendation:" in line and i + 1 < len(lines):
            state.workforce_recommendation = lines[i + 1].strip()

    return state