from crewai import Task
from agents.executive_agent import executive_agent


def build_executive_task(state):
    forecast_summary = getattr(
        state,
        "forecast_summary",
        "No forecast summary available."
    )

    staffing_summary = getattr(
        state,
        "staffing_summary",
        "No staffing summary available."
    )

    risk_level = getattr(
        state,
        "risk_level",
        "No risk level available."
    )

    risk_summary = getattr(
        state,
        "risk_summary",
        "No risk summary available."
    )

    risk_recommendation = getattr(
        state,
        "risk_recommendation",
        "No risk recommendation available."
    )

    cost_summary = getattr(
        state,
        "cost_summary",
        "No cost summary available."
    )

    cost_results = getattr(
        state,
        "cost_results",
        {}
    )

    memory_context = getattr(
        state,
        "memory_context",
        "No historical memory available."
    )

    rag_context = getattr(
        state,
        "rag_context",
        "No RAG context available."
    )

    vet_weeks = getattr(state, "vet_weeks", 0)
    vto_weeks = getattr(state, "vto_weeks", 0)

    return Task(
        description=f"""
        You are preparing an executive summary for a warehouse workforce forecasting and labor optimization system.

        STRICT GUARDRAILS:

        You are an AI operations decision-support assistant for a warehouse workforce forecasting dashboard.      
        You may only use the forecast summary, staffing summary, operational risk assessment, cost summary, cost results, retrieved operational context, and historical memory provided in this task.
        You must not invent forecast values, labor costs, cost savings, staffing decisions, business causes, company policies, HR rules, or operational facts that are not provided.
        You must not override the VET, VTO, NORMAL, MIXED, or Maintain Staffing recommendation produced by the forecast model, staffing task, or business rule engine.
        You must not describe this as an official Amazon system. 
        You must not provide HR, payroll, legal, medical, safety, or employment-policy advice.
        If the available information is incomplete, say the explanation is limited by the available forecast data.
        The final summary is decision-support only and should be reviewed by a human operations manager.
        You must refer to confidence as an operational confidence score, not as certainty or a guarantee of staffing success.
        You must not describe estimated labor cost impact as labor savings unless an explicit savings metric is provided in the task input.

        Staffing Signal Counts:
        - VET Weeks: {vet_weeks}
        - VTO Weeks: {vto_weeks}
        
        Forecast Summary:
        {forecast_summary}
        
        Staffing Summary:
        {staffing_summary}

        Operational Risk Assessment:
        - Risk Level: {risk_level}
        - Risk Summary: {risk_summary}
        - Risk Recommendation: {risk_recommendation}
        
        Cost Summary:
        {cost_summary}
        
        Cost Results:
        {cost_results}

        Retrieved Operational Context:
        {rag_context}
            
        Relevant Historical Memory:
        {memory_context}

 
        Write a concise business-facing executive summary for operations leadership.
        
        Include:
        1. Expected demand and labor risk
        2. Operational risk level and main risk drivers
        3. VET/VTO/Normal staffing recommendation
        4. Estimated labor cost impact
        5. Recommended management action
        6. Key assumptions and limitations

        Do not say staffing should simply be maintained if VET weeks or VTO weeks are present.
        If VET weeks are present, recommend preparing extra labor coverage.
        If VTO weeks are present, recommend planned labor reduction or voluntary time off.
        If both are present, explain the mixed staffing pattern.

        If VET weeks are greater than zero, do not say only "maintain current staffing levels."
        Instead, say "maintain baseline staffing while preparing targeted VET coverage."
        If VTO weeks are greater than zero, mention planned VTO or labor reduction.
        If both VET and VTO weeks are zero, then it is appropriate to say maintain current staffing levels.

        Use the phrase "workforce readiness" instead of "workforce skills" unless training or skill development is explicitly part of the scenario.

        Use the retrieved operational context to improve explanation quality, but do not invent facts or change the forecast, staffing, or cost calculations.
        
        Do not change the forecast, staffing recommendations, or cost calculations.
        Only explain the results clearly.

        Requirements:
        - maximum 6 bullet points
        - executive business language
        - concise operational tone
        - refer to confidence as an "operational confidence score"
        - do not describe confidence as certainty or a guarantee
        - avoid phrases like "confidence level in meeting staffing requirements"
        - if confidence is mentioned, say it supports planning reliability, not guaranteed outcomes
        - avoid filler or repetition
        - focus on actionable operational insight
        - highlight staffing risks if present
        - highlight labor cost concerns if present
        - mention workforce readiness
        - mention workload stability
        - mention operational confidence
        - reference historical operational similarities if relevant
        - incorporate workforce staffing intelligence into reasoning
        - do NOT use numbering
        - do NOT write long paragraphs
        - each bullet should be one concise sentence
        - avoid generic AI phrases
        - avoid motivational language
        - avoid speculative recommendations
        - avoid repeating the same operational insight
        - prioritize concise executive communication
        - refer to labor cost as "estimated labor cost impact" unless a separate savings value is explicitly provided
        - do not describe labor cost impact as "savings" unless the input data explicitly says it is savings
        - avoid phrases like "potential labor savings" when only estimated cost impact is provided
        - if discussing VTO, say it may support labor cost control, not guaranteed savings
        - include the operational risk level if available
        - do not invent additional risk factors beyond the provided risk assessment

        The summary should sound like an enterprise warehouse
        operations intelligence platform used by senior leadership.
        
        """,
                expected_output="""
        A concise executive summary written in business language for warehouse operations leadership.
        """,
        agent=executive_agent
    )

