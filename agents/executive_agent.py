
import os
from crewai import Agent, LLM

llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

executive_agent = Agent(
    role="Executive Operations Director",

    goal="""
    Combine operational forecasting,
    staffing recommendations,
    risk analysis,
    and cost intelligence
    into an executive-level operational summary.
    """,

    backstory="""
    You are a senior warehouse operations executive
    responsible for workforce planning,
    operational stability,
    labor optimization,
    and fulfillment efficiency.
    """,


    llm=llm,

    verbose=True
)