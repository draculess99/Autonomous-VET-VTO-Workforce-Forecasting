from graph.operational_state import OperationalState
from graph.operational_graph import run_operational_graph
# python test_operational_graph.py

state = OperationalState(
    peak_week=3,
    total_cost=19200,
    stress_band="Low",
    confidence_score=100,
    primary_risk_display="Minimal Operational Risk",
    vet_weeks=3,
    vto_weeks=0,
    memory_context="Past similar low-stress VET scenario was stable."
)

final_state = run_operational_graph(state)

print("\n==============================")
print("FORECAST SUMMARY")
print("==============================")
#print(final_state.forecast_summary)
print(final_state.get("forecast_summary", ""))

print("\n==============================")
print("STAFFING SUMMARY")
print("==============================")
#print(final_state.staffing_summary)
print(final_state.get("staffing_summary", ""))

print("\n==============================")
print("COST SUMMARY")
print("==============================")
#print(final_state.cost_summary)
print(final_state.get("cost_summary", ""))

print("\n==============================")
print("EXECUTIVE SUMMARY")
print("==============================")
# print(final_state.executive_summary)
print(final_state.get("executive_summary", ""))