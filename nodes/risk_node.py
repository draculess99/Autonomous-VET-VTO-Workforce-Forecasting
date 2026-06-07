def run_risk_node(state):
    """
    Evaluates operational risk based on workload stress, staffing signal,
    VET/VTO balance, confidence score, and memory context.
    """

    risk_drivers = []

    # Risk from stress band
    if state.stress_band in ["High", "Critical", "Severe"]:
        risk_drivers.append("High workload stress level")
    elif state.stress_band in ["Medium", "Moderate"]:
        risk_drivers.append("Moderate workload pressure")

    # Risk from confidence score
    if state.confidence_score < 0.60:
        risk_drivers.append("Low forecast confidence")
    elif state.confidence_score < 0.75:
        risk_drivers.append("Moderate forecast confidence")

    # Risk from VET/VTO balance
    if state.vet_weeks > state.vto_weeks:
        risk_drivers.append("Greater reliance on VET than VTO")
    elif state.vto_weeks > state.vet_weeks and state.stress_band in ["High", "Critical", "Severe"]:
        risk_drivers.append("Potentially unsafe VTO signal during high workload pressure")

    # Risk from primary risk display
    if state.primary_risk_display:
        risk_drivers.append(f"Primary risk indicator: {state.primary_risk_display}")

    # Determine risk level
    if len(risk_drivers) >= 3:
        risk_level = "High"
    elif len(risk_drivers) == 2:
        risk_level = "Medium"
    elif len(risk_drivers) == 1:
        risk_level = "Low"
    else:
        risk_level = "Low"

    # Build summary
    if risk_drivers:
        risk_summary = "Operational risk factors detected: " + "; ".join(risk_drivers) + "."
    else:
        risk_summary = "No major operational risk factors were detected based on the current forecast and staffing inputs."

    # Recommendation
    if risk_level == "High":
        risk_recommendation = (
            "Leadership review is recommended before applying the staffing recommendation. "
            "The system detected multiple operational stress indicators."
        )
    elif risk_level == "Medium":
        risk_recommendation = (
            "Operations should monitor staffing levels and workload volatility before finalizing the plan."
        )
    else:
        risk_recommendation = (
            "Risk appears manageable, but staffing decisions should still be reviewed by operations leadership."
        )

    state.risk_level = risk_level
    state.risk_summary = risk_summary
    state.risk_recommendation = risk_recommendation

    return state