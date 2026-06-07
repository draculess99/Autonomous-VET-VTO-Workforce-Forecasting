import os
from crewai import Agent, LLM

llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)
 

forecast_agent = Agent(

    role="Warehouse Forecast Analyst",

    goal="""
    Analyze warehouse demand forecasts
    and workforce planning risks.
    """,

    backstory="""
    Expert in warehouse staffing,
    VET/VTO planning,
    and operational forecasting.
    """,

    llm=llm,

    verbose=True
)