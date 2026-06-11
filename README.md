# Autonomous VET/VTO Workforce Forecasting System

A human-in-the-loop autonomous workforce planning system using XGBoost forecasting, agentic AI, guardrails, and a supervisor-led control layer to produce traceable VET/VTO staffing recommendations.

## Overview

This project is an AI-powered warehouse workforce forecasting and staffing decision-support system. It forecasts future workload demand, recommends VET, VTO, or Normal staffing actions, and explains the recommendation through an agentic AI workflow.

The project began as a traditional machine learning forecasting application and was later upgraded into a multi-agent decision-support architecture. The latest version adds an autonomous supervisor layer that reviews the completed workflow, validates guardrail status, assigns a final recommendation, records risk level, and stores a trace of the decision path.

The goal of the system is to move from prediction to action.

Instead of only forecasting workload, the application converts forecast outputs into operational staffing recommendations that a manager can review and act on.

---

## Project Purpose

Warehouse and fulfillment operations often need to decide whether to increase staffing, reduce excess labor, or maintain current staffing levels. These decisions are usually affected by expected workload, labor cost, operational stress, and risk.

This project demonstrates how machine learning and agentic AI can be combined to support workforce planning decisions.

The system helps answer:

* Is workload expected to increase or decrease?
* Should the site use VET, VTO, or maintain current staffing?
* What is the potential cost impact?
* What operational risk is associated with the recommendation?
* Can the decision be explained clearly to a human manager?
* Can the system show a trace of how the final recommendation was produced?

---

## Technology Stack

* Python
* Pandas
* NumPy
* Scikit-learn
* XGBoost
* Streamlit
* Flask
* Plotly
* LangGraph-style workflow
* CrewAI-style agentic design
* Pydantic
* RAG context layer
* GitHub Pages
* Docker / cloud deployment experiments

---

## Architecture Evolution

### 1. Basic Forecasting Version

The original version used machine learning to forecast future workload demand.

Core components:

* XGBoost forecasting model
* Weekly forecast output
* VET / VTO / Normal staffing logic
* Labor cost estimates
* Streamlit dashboard
* Flask API backend

This version answered:

> What workload is expected, and what staffing action should be considered?

---

### 2. Agentic AI Version

The project was then upgraded into an agentic decision-support system.

The agentic workflow interprets forecast outputs and produces an operational explanation.

Main workflow:

```text
XGBoost Forecast
   ↓
Forecast Node
   ↓
Staffing Node
   ↓
Risk Node
   ↓
Cost Node
   ↓
RAG Context Node
   ↓
Executive Summary Node
   ↓
Operational Memory
```

This version answered:

> Why does the staffing recommendation make sense operationally?

---

### 3. Autonomous Supervisor Version

The latest version adds an autonomous supervisor layer.

The supervisor does not replace the XGBoost model or the agentic workflow. Instead, it reviews the completed operational state and produces a final controlled output.

The autonomous supervisor provides:

* Final staffing recommendation
* Guardrail status
* Risk level
* Autonomous summary
* Agent trace
* Human-in-the-loop decision-support framing

Autonomous supervisor flow:

```text
LangGraph Operational Workflow
   ↓
Autonomous Supervisor
   ↓
Guardrail Review
   ↓
Final Recommendation
   ↓
Risk Level
   ↓
Autonomous Summary
   ↓
Traceable Decision Output
```

This version answers:

> Did the workflow complete safely, did the guardrails pass, and what final recommendation should be shown for human review?

---

## How This Differs from the Agentic Version

The earlier agentic version explains the forecast through separate forecast, staffing, risk, cost, RAG, and executive-summary nodes.

This autonomous version adds a supervisor-led control layer on top of that workflow.

The supervisor reviews the completed operational state, checks whether required outputs are present, confirms guardrail status, assigns a final recommendation, records risk level, and stores a traceable decision path for human review.

---

## Key Features

* XGBoost workload forecasting
* VET / VTO / Normal staffing recommendation logic
* Streamlit dashboard
* Flask API backend
* LangGraph-style operational workflow
* CrewAI-inspired multi-agent decision layer
* Guardrails for forecast inputs and staffing decisions
* RAG context node
* Operational memory
* Executive AI summary
* Autonomous supervisor output
* Traceable agent workflow
* Human-in-the-loop decision-support explanation

---

## Core Staffing Actions

| Action | Meaning                                                                   |
| ------ | ------------------------------------------------------------------------- |
| VET    | Voluntary Extra Time / increase labor coverage                            |
| VTO    | Voluntary Time Off / reduce excess staffing                               |
| NORMAL | Maintain current staffing level                                           |
| MIXED  | Combination of targeted VET and selective VTO across the forecast horizon |

---

## Guardrails

The system includes guardrails to prevent unreliable or unsupported outputs.

The guardrail layer validates:

* Forecast input payloads
* Forecast horizon length
* Economic and operational input ranges
* Staffing decisions
* Predicted demand values
* Estimated cost values
* AI-generated explanation length
* Human-review disclaimer

The system only allows valid staffing decisions such as:

```text
VET
VTO
NORMAL
```

The autonomous supervisor then adds another control layer by checking whether the completed workflow state contains the required forecast, staffing, risk, and summary outputs.

---

## Autonomous Supervisor Output

The autonomous supervisor produces a compact decision-control summary.

Example output:

```text
Final Recommendation: VET
Guardrail Status: Passed
Risk Level: Medium
```

The supervisor also generates an autonomous summary explaining why the recommendation was selected and why it should be reviewed by a human operations manager before action is taken.

---

## Agent Trace

The project includes a traceable decision path so the workflow is not a black box.

Example trace:

```text
Supervisor started autonomous VET/VTO workflow.
Forecast output detected from forecasting node.
Staffing recommendation detected from staffing node.
Supervisor selected final recommendation: VET.
Risk level detected from risk node: Medium.
Supervisor guardrail review passed.
Autonomous summary generated for human review.
Supervisor completed autonomous VET/VTO workflow.
```


See the full trace explanation in `docs/autonomous_supervisor_trace.md`.

---

## System Flow

```text
User Scenario Input
   ↓
Streamlit Dashboard
   ↓
Payload Guardrails
   ↓
Flask Forecast API
   ↓
XGBoost Forecast
   ↓
Weekly Staffing Recommendation
   ↓
Staffing Guardrails
   ↓
LangGraph Operational Workflow
   ↓
Forecast / Staffing / Risk / Cost / RAG / Executive Nodes
   ↓
Autonomous Supervisor
   ↓
Final Recommendation + Risk + Guardrail Status + Trace
   ↓
Human Review
```

---

## Screenshots

### Forecast Dashboard

The dashboard displays the 12-week demand forecast, weekly labor cost, and cumulative future cost.

![Forecast Dashboard](images/forecast_dashboard.png)

### Operational Recommendations

The recommendation layer converts forecast results into VET, VTO, Normal, or Mixed staffing guidance.

![Operational Recommendations](images/operational_recommendations.png)

### AI Operational Decision Summary

The AI decision summary explains the operational meaning of the forecast, staffing recommendation, risk level, and cost impact.

![AI Operational Decision Summary](images/ai_operational_decision_summary.png)

### Autonomous Control Layer

The autonomous supervisor reviews the completed workflow, confirms guardrail status, assigns the final recommendation, records risk level, and stores a traceable decision path.

![Autonomous Control Layer](images/autonomous_control_layer.png)

---

## Documentation

- [Current Agentic Flow](docs/current_agentic_flow.md)
- [Autonomous Supervisor Trace](docs/autonomous_supervisor_trace.md)

---

## Why This Project Matters

This project demonstrates how machine learning forecasts can be converted into operational decisions.

The machine learning model predicts workload. The agentic workflow explains the forecast and staffing recommendation. The autonomous supervisor adds a control layer that checks the workflow, confirms guardrail status, records risk level, and stores a trace.

This makes the system more than a forecasting dashboard. It becomes a human-in-the-loop workforce decision-support system.

The key contribution is:

> From prediction to action: converting workload forecasts into traceable staffing recommendations using agentic AI and an autonomous supervisor layer.

---

## Human-in-the-Loop Design

This system is designed for decision support only.

It does not automatically execute staffing changes. Final staffing decisions should be reviewed by a human operations manager using current site conditions, attendance, safety requirements, labor rules, and business constraints.

The autonomous supervisor helps organize and validate the recommendation, but it does not replace human judgment.

---

## Example Business Use Case

A warehouse operations manager wants to forecast workload for the next 12 weeks.

The system:

1. Forecasts weekly workload demand.
2. Identifies high-demand and low-demand weeks.
3. Recommends VET, VTO, Normal, or Mixed staffing actions.
4. Estimates labor cost impact.
5. Checks staffing decisions against guardrails.
6. Generates an AI operational decision summary.
7. Runs an autonomous supervisor control check.
8. Displays a trace of the decision workflow.

---

## Repository Structure

```text
agents/                 Agent definitions
tasks/                  Agent task definitions
nodes/                  Operational workflow nodes
graph/                  Operational graph, state, and autonomous supervisor
guardrails/             Input, staffing, and AI output guardrails
memory/                 Operational memory logic
rag_docs/               RAG reference material
docs/                   Architecture notes and workflow trace documentation
streamlit_app.py        Streamlit dashboard
flask_api.py            Forecast API backend
crew_runner.py          Runs operational agentic workflow
scenario_templates.tsv  Scenario rule engine data
```

---

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```
Start the Flask backend:
```bash
python flask_api.py
```
Start the Streamlit dashboard:
```bash
streamlit run streamlit_app.py
```
Optional environment variables:
```bash
GEMINI_API_KEY
GROQ_API_KEY
```
---

## Current Status

The project currently includes:

* Working forecasting dashboard
* Forecast input guardrails
* Staffing output guardrails
* AI operational decision summary
* LangGraph-style operational workflow
* Autonomous supervisor output
* Final recommendation display
* Risk level display
* Guardrail status display
* Autonomous agent trace

The autonomous upgrade is complete at portfolio-demo level.

---

## Future Extension: Hospital Staffing

The same architecture can be adapted to hospital or emergency department staffing.

The pattern would become:

```text
Patient demand forecast
   ↓
Staffing level recommendation
   ↓
Cost / coverage / risk review
   ↓
Autonomous supervisor
   ↓
Traceable staffing recommendation
```

This makes the project reusable beyond warehouse staffing and demonstrates how the architecture can be transferred to other workforce planning domains.

---

## Autonomous Supervisor Trace

The autonomous supervisor records a trace of the decision workflow so the final recommendation is not a black-box output.

Example trace:

```text
Supervisor started autonomous VET/VTO workflow.
Forecast output detected from forecasting node.
Staffing recommendation detected from staffing node.
Supervisor detected mixed staffing pattern: 1 VET week(s) and 2 VTO week(s).
Risk level detected from risk node: Low.
Supervisor guardrail review passed.
Autonomous summary generated for human review.
Supervisor completed autonomous VET/VTO workflow.

```

  → full trace explanation
  → mixed staffing logic
  → human-in-the-loop design
  → example output
  → why the trace matters

---

## Portfolio Summary

This project demonstrates applied AI engineering across forecasting, decision logic, guardrails, agentic workflows, and autonomous supervision.

A concise description:

> I built a human-in-the-loop autonomous workforce planning system that uses XGBoost to forecast workload, agentic AI to explain staffing decisions, and an autonomous supervisor to validate guardrails, assign final recommendations, and record a transparent decision trace.
