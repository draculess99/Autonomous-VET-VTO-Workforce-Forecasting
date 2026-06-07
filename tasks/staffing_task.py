from crewai import Task
from agents.staffing_agent import staffing_agent


def build_staffing_task(
    peak_week,
    total_cost,
    stress_band,
    confidence,
    primary_risk_display,
    vet_weeks,
    vto_weeks
):

    return Task(

        description=f"""
        Analyze warehouse staffing requirements
        and workforce planning strategy.

        Forecast Details:
        - Peak Week: {peak_week}
        - Total Labor Cost: ${total_cost:,.0f}
        - Stress Level: {stress_band}
        - Operational Confidence Score: {confidence:.0f}%
        - Primary Operational Risk Driver:
          {primary_risk_display}
        - VET Weeks: {vet_weeks}
        - VTO Weeks: {vto_weeks}

        Analyze:
        - staffing balance
        - workforce readiness
        - VET/VTO strategy
        - staffing flexibility
        - operational labor planning

        Recommend workforce actions
        and operational staffing strategy.
        
        STRICT STAFFING GUARDRAILS:

        You may only recommend one of these staffing actions:
        - VET
        - VTO
        - Maintain Staffing
        
        Do not recommend layoffs, hiring, mandatory overtime, discipline, HR action, payroll action, legal action, or safety-policy changes.
        
        Do not invent staffing values, cost savings, business causes, company policies, or operational facts that are not provided.
        
        Base the recommendation only on the provided peak week, total labor cost, stress level, confidence score, primary risk driver, VET weeks, and VTO weeks.
        
        If VET Weeks is greater than zero and VTO Weeks is zero, prefer VET.

        If VTO Weeks is greater than zero and VET Weeks is zero, prefer VTO.
        
        If both VET Weeks and VTO Weeks are greater than zero and VET Weeks is greater than VTO Weeks, use VET as the Recommended Action and describe the mixed staffing pattern in the Workforce Recommendation field.
        
        If both VET Weeks and VTO Weeks are greater than zero and VTO Weeks is greater than VET Weeks, use VTO as the Recommended Action and describe the mixed staffing pattern in the Workforce Recommendation field.
        
        If both VET Weeks and VTO Weeks are greater than zero and the counts are equal, use Maintain Staffing as the Recommended Action and describe the mixed staffing pattern in the Workforce Recommendation field.
        
        If both VET Weeks and VTO Weeks are zero, use Maintain Staffing.
        
        You MUST return ONLY the following format.
        
        Do NOT include bullet points.
        Do NOT include introductions.
        Do NOT include explanations outside this structure.
        Do NOT include extra commentary.
        
        Recommended Action:
        <VET / VTO / Maintain Staffing>
        
        Staffing Risk Level:
        <Low / Medium / High>
        
        Operational Concern:
        <one concise operational concern>
        
        Operational Reason:
        <one concise sentence>
        
        Workforce Recommendation:
        <one concise sentence>""",

        expected_output="""
        Recommended Action:
        <VET / VTO / Maintain Staffing>
        
        Staffing Risk Level:
        <Low / Medium / High>
        
        Operational Concern:
        <operational concern>
        
        Operational Reason:
        <one concise sentence>
        
        Workforce Recommendation:
        <one concise sentence>
        """,

        agent=staffing_agent
    )