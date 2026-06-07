# operational_state.py

#from pydantic import BaseModel
from pydantic import BaseModel, Field


class OperationalState(BaseModel):
    # -----------------------------------
    # Original Forecast / Scenario Inputs
    # -----------------------------------

    peak_week: int
    total_cost: float
    stress_band: str
    confidence_score: float
    primary_risk_display: str
    vet_weeks: int
    vto_weeks: int

    
    # -----------------------------------
    # Retrieved Historical Memory
    # -----------------------------------

    memory_context: str = ""

    # -----------------------------------
    # Forecast Node Output
    # -----------------------------------

    forecast_summary: str = ""
    forecast_risk_signal: str = ""
    forecast_confidence: float = 0.0

    # -----------------------------------
    # Staffing Node Output
    # -----------------------------------

    staffing_summary: str = ""
    staffing_action: str = ""
    staffing_risk_level: str = ""
    operational_concern: str = ""
    operational_reason: str = ""
    workforce_recommendation: str = ""

    # -----------------------------------
    # Cost Node Output
    # -----------------------------------

    cost_summary: str = ""
    cost_results: dict = {}

    # -----------------------------------
    # RAG Node Output
    # -----------------------------------

    rag_context: str = ""
    
    # -----------------------------------
    # Executive Node Output
    # -----------------------------------

    executive_summary: str = ""


    risk_level: str = ""
    risk_summary: str = ""
    risk_recommendation: str = ""

    # -----------------------------------
    # Autonomous Supervisor Output
    # -----------------------------------

    guardrail_status: str = ""
    final_recommendation: str = ""
    autonomous_summary: str = ""
    trace: list[str] = Field(default_factory=list)