# guardrails.py

from typing import Dict, Any, List


ALLOWED_DECISIONS = {"VET", "VTO", "NORMAL"}


def validate_forecast_payload(payload):
    """
    Validate nested forecast payload from Streamlit before sending to Flask API.
    Expected structure:

    payload = {
        "weeks": int,
        "inputs": {
            "temperature": [...],
            "fuel_price": [...],
            "cpi": [...],
            "unemployment": [...],
            "isholiday": [...]
        },
        "settings": {
            ...
        }
    }
    """

    errors = []

    # -----------------------------
    # Validate weeks
    # -----------------------------
    weeks = payload.get("weeks")

    if weeks is None:
        errors.append("Missing required field: weeks.")
    elif not isinstance(weeks, int):
        errors.append("weeks must be an integer.")
    elif weeks < 1 or weeks > 52:
        errors.append("weeks must be between 1 and 52.")

    # -----------------------------
    # Validate inputs object
    # -----------------------------
    inputs = payload.get("inputs")

    if inputs is None or not isinstance(inputs, dict):
        errors.append("Missing or invalid inputs section.")
        return {
            "valid": False,
            "errors": errors,
            "safe_payload": None
        }

    required_input_fields = {
        "temperature": (-40, 130),
        "fuel_price": (0, 20),
        "cpi": (0, 500),
        "unemployment": (0, 30),
        "isholiday": (0, 1),
    }

    for field, (min_val, max_val) in required_input_fields.items():
        values = inputs.get(field)

        if values is None:
            errors.append(f"Missing required field: inputs.{field}.")
            continue

        if not isinstance(values, list):
            errors.append(f"inputs.{field} must be a list.")
            continue

        if isinstance(weeks, int) and len(values) != weeks:
            errors.append(
                f"inputs.{field} must contain exactly {weeks} values."
            )

        for value in values:
            if not isinstance(value, (int, float)):
                errors.append(f"inputs.{field} contains a non-numeric value.")
                continue

            if value < min_val or value > max_val:
                errors.append(
                    f"inputs.{field} contains out-of-range value {value}. "
                    f"Allowed range: {min_val} to {max_val}."
                )

    # -----------------------------
    # Validate settings object
    # -----------------------------
    settings = payload.get("settings")

    if settings is None or not isinstance(settings, dict):
        errors.append("Missing or invalid settings section.")
    else:
        numeric_settings = {
            "workers_per_unit": (1, 1_000_000),
            "overtime_labor_cost_per_worker": (0, 500),
            "hourly_labor_cost_per_worker": (0, 500),
        }

        for field, (min_val, max_val) in numeric_settings.items():
            value = settings.get(field)

            if value is None:
                errors.append(f"Missing required setting: settings.{field}.")
                continue

            if not isinstance(value, (int, float)):
                errors.append(f"settings.{field} must be numeric.")
                continue

            if value < min_val or value > max_val:
                errors.append(
                    f"settings.{field} contains out-of-range value {value}. "
                    f"Allowed range: {min_val} to {max_val}."
                )

    if errors:
        return {
            "valid": False,
            "errors": errors,
            "safe_payload": None
        }

    return {
        "valid": True,
        "errors": [],
        "safe_payload": payload
    }


def validate_staffing_decisions(forecast_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates model output and staffing decisions before the AI layer explains them.
    Ensures the agent cannot fabricate unsupported VET/VTO recommendations.
    """

    errors = []

    for i, row in enumerate(forecast_rows):
        decision = str(row.get("decision", "")).upper()

        if decision not in ALLOWED_DECISIONS:
            errors.append(
                f"Week {i + 1}: invalid staffing decision '{decision}'. "
                f"Allowed decisions are VET, VTO, NORMAL."
            )

        predicted_demand = row.get("predicted_demand")

        if predicted_demand is None:
            errors.append(f"Week {i + 1}: missing predicted_demand.")
        elif not isinstance(predicted_demand, (int, float)):
            errors.append(f"Week {i + 1}: predicted_demand must be numeric.")
        elif predicted_demand < 0:
            errors.append(f"Week {i + 1}: predicted_demand cannot be negative.")

        estimated_cost = row.get("estimated_cost")

        if estimated_cost is not None:
            if not isinstance(estimated_cost, (int, float)):
                errors.append(f"Week {i + 1}: estimated_cost must be numeric.")
            elif estimated_cost < 0:
                errors.append(f"Week {i + 1}: estimated_cost cannot be negative.")

    if errors:
        return {
            "valid": False,
            "errors": errors,
        }

    return {
        "valid": True,
        "errors": [],
    }


def constrain_ai_summary(
    ai_text: str,
    allowed_decisions=None,
    max_words: int = 180,
    add_disclaimer: bool = False
) -> str:
    """
    Final output guardrail for the AI-generated explanation.
    Keeps the summary concise. Disclaimer can be shown separately in Streamlit.
    """

    if not ai_text or not isinstance(ai_text, str):
        return (
            "AI summary unavailable. Please rely on the forecast table, staffing "
            "recommendation logic, and cost results shown above."
        )

    words = ai_text.split()

    if len(words) > max_words:
        ai_text = " ".join(words[:max_words]) + "..."

    if add_disclaimer:
        ai_text += (
            "\n\nNote: This AI explanation is decision-support only. "
            "Final staffing decisions should be reviewed by a human operations manager "
            "using current site conditions, attendance, safety, and business constraints."
        )

    return ai_text.strip()