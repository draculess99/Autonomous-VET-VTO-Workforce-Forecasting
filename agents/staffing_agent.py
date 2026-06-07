import os
from crewai import Agent, LLM

llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

staffing_agent = Agent(
    role="Warehouse Workforce Planner",

    goal="""
    Recommend workforce actions including:
    VET,
    VTO,
    staffing stabilization,
    and operational labor balancing.
    """,

    backstory="""
    You specialize in warehouse staffing strategy,
    labor balancing,
    workforce stabilization,
    and operational labor planning.
    """,


    lm=llm,

    verbose=True
)