# nodes/cost_node.py


def run_cost_node(state):
    """
    Cost node for the VET/VTO workforce forecasting project.

    This node reads the existing forecast summary fields from OperationalState
    and creates a business-facing cost summary.

    It does not change the forecast, staffing decision, or VET/VTO logic.
    """

    try:
        vet_weeks = int(getattr(state, "vet_weeks", 0))
        vto_weeks = int(getattr(state, "vto_weeks", 0))
        total_cost = float(getattr(state, "total_cost", 0))
        peak_week = int(getattr(state, "peak_week", 0))
        stress_band = getattr(state, "stress_band", "Unknown")
        confidence_score = float(getattr(state, "confidence_score", 0))

        # Current state does not yet carry normal_weeks, total_extra_workers,
        # or total_workers_reduced, so we keep this version simple and safe.
        net_cost_impact = total_cost

        if vet_weeks > 0 and vto_weeks == 0:
            cost_direction = "additional labor cost"
            cost_interpretation = (
                "The forecast indicates staffing pressure from high-demand weeks, "
                "so the cost impact is mainly driven by VET/overtime coverage."
            )
        elif vto_weeks > 0 and vet_weeks == 0:
            cost_direction = "potential labor savings"
            cost_interpretation = (
                "The forecast indicates lower-demand weeks, so the cost impact is "
                "mainly driven by opportunities to reduce excess labor through VTO."
            )
        elif vet_weeks > 0 and vto_weeks > 0:
            cost_direction = "mixed labor cost impact"
            cost_interpretation = (
                "The forecast contains both high-demand and low-demand weeks, so "
                "management should balance VET coverage against VTO savings."
            )
        else:
            cost_direction = "stable labor cost impact"
            cost_interpretation = (
                "The forecast does not show major VET or VTO pressure, so labor cost "
                "impact is expected to remain relatively stable."
            )

        state.cost_results = {
            "vet_weeks": vet_weeks,
            "vto_weeks": vto_weeks,
            "total_cost": total_cost,
            "net_cost_impact": net_cost_impact,
            "peak_week": peak_week,
            "stress_band": stress_band,
            "confidence_score": confidence_score,
            "cost_direction": cost_direction,
        }

        state.cost_summary = (
            f"The projected labor cost impact is ${net_cost_impact:,.0f}. "
            f"The scenario includes {vet_weeks} VET week(s) and {vto_weeks} VTO week(s), "
            f"with peak demand expected around week {peak_week}. "
            f"The stress band is '{stress_band}' with a confidence score of "
            f"{confidence_score:.2f}. "
            f"This represents a {cost_direction}. {cost_interpretation}"
        )

    except Exception as e:
        state.cost_summary = (
            "Cost analysis could not be completed. "
            f"Technical error: {str(e)}"
        )
        state.cost_results = {
            "error": str(e)
        }

    return state