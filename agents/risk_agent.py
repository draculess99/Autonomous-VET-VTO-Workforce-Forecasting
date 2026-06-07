

import os
from crewai import Agent, LLM

llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)


risk_agent = Agent(
    role="Operational Risk Monitoring Specialist",

    goal="""
    Detect operational risks,
    workload instability,
    staffing threats,
    and warehouse operational stress indicators.
    """,

    backstory="""
    You specialize in warehouse operational risk analysis,
    identifying volatility,
    congestion,
    labor shortages,
    and fulfillment instability.
    """,


    llm=llm,

    verbose=True
)