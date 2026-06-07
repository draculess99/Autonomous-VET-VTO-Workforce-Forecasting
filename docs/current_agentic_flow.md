# Current Agentic VET/VTO Flow

This document explains the current agentic architecture before upgrading the system into an autonomous supervisor-led workflow.

## Current System Purpose

The VET/VTO system forecasts workload and converts the forecast into a staffing recommendation.

The system moves from prediction to action:

1. XGBoost forecasts workload.
2. Staffing logic recommends VET, VTO, or NORMAL.
3. Guardrails validate the input and staffing outputs.
4. The AI layer explains the recommendation.
5. Streamlit displays the final result.

## Current Architecture

Input data
   ↓
Streamlit app
   ↓
Payload validation guardrails
   ↓
Flask API / forecast logic
   ↓
XGBoost forecast
   ↓
Staffing recommendation logic
   ↓
Staffing decision guardrails
   ↓
AI explanation / CrewAI layer
   ↓
Final explanation guardrail
   ↓
Streamlit output

## Existing Guardrails

The current guardrail layer performs three main jobs:

1. It validates the forecast payload before sending it to the forecast API.
2. It validates staffing decisions so only VET, VTO, or NORMAL are allowed.
3. It constrains the AI summary so the explanation remains controlled and suitable for decision support.

## Current Limitation

The current system is agentic, but the workflow is not yet fully supervisor-led.

The next step is to add an autonomous supervisor that coordinates the workflow, checks whether each stage completed correctly, records a trace, and decides whether the recommendation should proceed, warn, or stop.

## Next Upgrade

The autonomous version will add:

- Supervisor Agent
- workflow trace
- guardrail status
- risk level
- final recommendation
- human-in-the-loop explanation

The goal is not to replace XGBoost or CrewAI. The goal is to coordinate the existing forecast, decision, guardrail, and explanation layers into a traceable autonomous workflow.