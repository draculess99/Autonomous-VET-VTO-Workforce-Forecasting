from crewai import Task
from agents.risk_agent import risk_agent


def build_risk_task():
    return Task(
        description="""
        Review the warehouse workforce forecast and staffing recommendation
        for operational risk.

        Identify risks such as:
        - workload instability
        - staffing shortage risk
        - excessive VET dependency
        - inappropriate VTO recommendation
        - peak demand pressure
        - congestion risk
        - labor cost stress
        - fulfillment delay risk

        Explain whether the current staffing recommendation appears low risk,
        medium risk, or high risk from an operations planning perspective.
        """,

        expected_output="""
        A concise operational risk assessment that includes:
        - risk level
        - key risk drivers
        - staffing concerns
        - operational warning signs
        - recommendation for leadership review if needed
        """,

        agent=risk_agent
    )