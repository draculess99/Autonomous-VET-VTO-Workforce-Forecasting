
import os
from crewai import Agent, LLM

llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

cost_agent = Agent(
    role="Labor Cost Optimization Analyst",

    goal="""
    Evaluate labor costs,
    overtime exposure,
    staffing efficiency,
    and operational budget concerns.
    """,

    backstory="""
    You are an expert in warehouse labor economics,
    workforce optimization,
    overtime management,
    and fulfillment operational budgeting.
    """,

    llm=llm,
    
    verbose=True
)