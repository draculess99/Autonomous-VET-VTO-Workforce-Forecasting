from crewai import Crew

from agents.forecast_agent import forecast_agent
from tasks.forecast_task import forecast_task

crew = Crew(

    agents=[forecast_agent],

    tasks=[forecast_task],

    verbose=True
)

result = crew.kickoff()

print(result)