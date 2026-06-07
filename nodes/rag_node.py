# nodes/rag_node.py

from pathlib import Path


def run_rag_node(state):
    """
    Simple RAG context node for the VET/VTO workforce forecasting project.

    This node retrieves relevant project/operations context from local text files
    and stores the combined context in state.rag_context.

    It does not change forecasts, staffing recommendations, or cost calculations.
    """

    try:
        docs_path = Path("rag_docs")

        if not docs_path.exists():
            state.rag_context = (
                "No RAG documents folder found. "
                "Executive summary should rely only on forecast, staffing, and cost state."
            )
            return state

        vet_weeks = int(getattr(state, "vet_weeks", 0))
        vto_weeks = int(getattr(state, "vto_weeks", 0))
        stress_band = getattr(state, "stress_band", "Unknown")
        cost_summary = getattr(state, "cost_summary", "")

        selected_files = [
            "forecasting_methodology.txt",
            "cost_model_assumptions.txt",
            "project_limitations.txt",
            "warehouse_operations_notes.txt",
        ]

        if vet_weeks > 0 or vto_weeks > 0:
            selected_files.insert(0, "vet_vto_policy_notes.txt")

        context_blocks = []

        for file_name in selected_files:
            file_path = docs_path / file_name

            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                context_blocks.append(
                    f"--- {file_name} ---\n{content}"
                )

        state.rag_context = f"""
RAG Context Retrieved for Current Scenario:

Scenario Signals:
- VET weeks: {vet_weeks}
- VTO weeks: {vto_weeks}
- Stress band: {stress_band}
- Cost summary: {cost_summary}

Retrieved Knowledge:
{chr(10).join(context_blocks)}
"""

    except Exception as e:
        state.rag_context = (
            "RAG context could not be retrieved. "
            f"Technical error: {str(e)}"
        )

    return state