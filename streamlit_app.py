#!/usr/bin/env python
# coding: utf-8

# # Run Streamllit App
# 
# ```bash
# streamlit run streamlit_app.py
# ```
# 

# In[ ]:


#from google import genai
import os

# ==========================================================
# streamlit_app.py
# Warehouse Workforce Forecast Dashboard
# FULL VERSION with SIMPLE + ADVANCED WEEKLY TABLE MODE
# ==========================================================
import time
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

from crew_runner import run_operational_crew
from guardrails.guardrails import (
    validate_forecast_payload,
    validate_staffing_decisions,
    constrain_ai_summary
)

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="Autonomous AI Workforce Planning",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Autonomous AI Workforce Forecasting & VET/VTO Decision Support")

st.caption(
    "A human-in-the-loop autonomous workforce planning system that uses XGBoost "
    "to forecast workload, agentic AI to explain staffing decisions, and an autonomous "
    "supervisor to validate guardrails, assign final recommendations, and record a "
    "transparent decision trace."
)

# -----------------------------------
# SESSION STATE INIT
# -----------------------------------

st.markdown("""
<style>
/* Target sidebar expander headers */
section[data-testid="stSidebar"] div[data-testid="stExpander"] details {
    border: 1px solid #8a6d1d;
    border-radius: 10px;
    background: rgba(138,109,29,0.18);
    margin-bottom: 10px;
}

section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {
    background: rgba(138,109,29,0.35);
    color: #ffd76a;
    border-radius: 10px;
    padding: 6px 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div.stButton > button:first-child {
    background: linear-gradient(135deg,#198754,#157347);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.55rem 1rem;
    font-weight: 700;
    width: 100%;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}

div.stButton > button:first-child:hover {
    background: linear-gradient(135deg,#20a464,#198754);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# LOAD SCENARIO CSV
# ----------------------------------------------------------
@st.cache_data
def load_scenarios():
    return pd.read_csv("scenario_templates.tsv", sep="\t")

scenario_df = load_scenarios()

# ----------------------------------------------------------
# GEMINI HELPER FUNCTIONS
# ----------------------------------------------------------
# ----------------------------------------------------------
# GEMINI HELPER FUNCTIONS
# ----------------------------------------------------------
def get_gemini_explanation(
    result_df,
    rec,
    stress_band,
    velocity_pct,
    shipping_delay_pct,
    congestion_pct,
    logistics_stress_pct
):

    try:

        from google import genai
        import os

        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        # -----------------------------
        # Forecast Metrics
        # -----------------------------
        total_cost = result_df["estimated_cost"].sum()

        peak = result_df["predicted_demand"].max()

        avg = result_df["predicted_demand"].mean()

        peak_row = result_df.loc[
            result_df["predicted_demand"].idxmax()
        ]

        peak_week = int(peak_row["week"])

                # -----------------------------
        # Forecast Trend Direction
        # -----------------------------

        trend_pct = (
            (
                result_df["predicted_demand"].iloc[-1]
                -
                result_df["predicted_demand"].iloc[0]
            )
            /
            result_df["predicted_demand"].iloc[0]
        ) * 100

        if trend_pct > 5:
            trend_direction = "Rising"

        elif trend_pct < -5:
            trend_direction = "Declining"

        else:
            trend_direction = "Stable"

        # -----------------------------
        # Forecast Volatility
        # -----------------------------

        volatility = (
            result_df["predicted_demand"].std()
            /
            result_df["predicted_demand"].mean()
        ) * 100

        if volatility > 8:
            volatility_band = "High"

        elif volatility > 4:
            volatility_band = "Moderate"

        else:
            volatility_band = "Low"

        # -----------------------------
        # Consecutive Decision Streaks
        # -----------------------------

        max_vet_streak = 0
        current_vet = 0

        for d in result_df["decision"]:

            if d == "VET":

                current_vet += 1

                max_vet_streak = max(
                    max_vet_streak,
                    current_vet
                )

            else:

                current_vet = 0

        max_vto_streak = 0
        current_vto = 0

        for d in result_df["decision"]:

            if d == "VTO":

                current_vto += 1

                max_vto_streak = max(
                    max_vto_streak,
                    current_vto
                )

            else:

                current_vto = 0

        demand_band = classify_demand_band(result_df)

        cost_band = classify_cost_band(result_df)

        action = rec["action"]

        rule_text = rec["final_recommendation"]

        # -----------------------------
        # Operational Stress Summary
        # -----------------------------
        if isinstance(velocity_pct, list):
            avg_velocity = sum(velocity_pct) / len(velocity_pct)
            avg_shipping = sum(shipping_delay_pct) / len(shipping_delay_pct)
            avg_congestion = sum(congestion_pct) / len(congestion_pct)
            avg_logistics = sum(logistics_stress_pct) / len(logistics_stress_pct)
        else:
            avg_velocity = velocity_pct
            avg_shipping = shipping_delay_pct
            avg_congestion = congestion_pct
            avg_logistics = logistics_stress_pct

        # -----------------------------
        # Controlled Prompt
        # -----------------------------
        prompt = f"""
You are an operations forecasting analyst for a warehouse workforce planning system.

Your role is to explain forecast results clearly to warehouse leadership.

You MUST only use the supplied metrics.
Do NOT invent trends, causes, percentages, or operational assumptions.

FORECAST METRICS

- Peak forecast week: Week {peak_week}
- Peak forecast demand index: {peak:,.0f}
- Average forecast demand index: {avg:,.0f}
- Demand classification: {demand_band}
- Labor cost classification: {cost_band}
- Projected labor cost impact: ${total_cost:,.0f}
- Recommended staffing action: {action}

OPERATIONAL STRESS METRICS

- Operational stress level: {stress_band}
- Demand velocity pressure: {avg_velocity:.1f}%
- Shipping delay pressure: {avg_shipping:.1f}%
- Warehouse congestion pressure: {avg_congestion:.1f}%
- Logistics stress pressure: {avg_logistics:.1f}%

FORECAST INTELLIGENCE METRICS

- Forecast trend direction: {trend_direction}
- Forecast volatility level: {volatility_band}
- Maximum consecutive VET weeks: {max_vet_streak}
- Maximum consecutive VTO weeks: {max_vto_streak}

RULE-BASED RECOMMENDATION

{rule_text}

RESPONSE REQUIREMENTS

1. Write exactly 5 sentences.
2. Use professional operations language.
3. Refer to demand as forecast demand or workload.
4. Do NOT mention AI, models, algorithms, or predictions.
5. Do NOT exaggerate urgency.
6. If operational stress is High, mention operational coordination and backlog risk carefully.
7. If action is VET:
   recommend targeted overtime planning before peak demand periods.
8. If action is VTO:
   recommend reducing excess staffing cautiously to avoid understaffing.
9. If action is NORMAL:
   recommend maintaining current staffing strategy with continued monitoring.
10. Mention labor cost discipline if cost band is High.
11. Keep the tone concise, executive, and operational.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:

        return f"Gemini unavailable: {str(e)}"

# ----------------------------------------------------------
# GROQ HELPER FUNCTIONS
# ----------------------------------------------------------
def get_groq_explanation(
    result_df,
    rec,
    stress_band,
    velocity_pct,
    shipping_delay_pct,
    congestion_pct,
    logistics_stress_pct
):

    try:

        from groq import Groq
        import os

        client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        # -----------------------------------
        # Forecast Metrics
        # -----------------------------------

        total_cost = result_df["estimated_cost"].sum()

        peak = result_df["predicted_demand"].max()

        avg = result_df["predicted_demand"].mean()

        peak_row = result_df.loc[
            result_df["predicted_demand"].idxmax()
        ]

        peak_week = int(peak_row["week"])

                # -----------------------------
        # Forecast Trend Direction
        # -----------------------------

        trend_pct = (
            (
                result_df["predicted_demand"].iloc[-1]
                -
                result_df["predicted_demand"].iloc[0]
            )
            /
            result_df["predicted_demand"].iloc[0]
        ) * 100

        if trend_pct > 5:
            trend_direction = "Rising"

        elif trend_pct < -5:
            trend_direction = "Declining"

        else:
            trend_direction = "Stable"

        # -----------------------------
        # Forecast Volatility
        # -----------------------------

        volatility = (
            result_df["predicted_demand"].std()
            /
            result_df["predicted_demand"].mean()
        ) * 100

        if volatility > 8:
            volatility_band = "High"

        elif volatility > 4:
            volatility_band = "Moderate"

        else:
            volatility_band = "Low"

        # -----------------------------
        # Consecutive Decision Streaks
        # -----------------------------

        max_vet_streak = 0
        current_vet = 0

        for d in result_df["decision"]:

            if d == "VET":

                current_vet += 1

                max_vet_streak = max(
                    max_vet_streak,
                    current_vet
                )

            else:

                current_vet = 0

        max_vto_streak = 0
        current_vto = 0

        for d in result_df["decision"]:

            if d == "VTO":

                current_vto += 1

                max_vto_streak = max(
                    max_vto_streak,
                    current_vto
                )

            else:

                current_vto = 0

        demand_band = classify_demand_band(result_df)

        cost_band = classify_cost_band(result_df)

        action = rec["action"]

        # -----------------------------------
        # Stress Metrics
        # -----------------------------------

        if isinstance(velocity_pct, list):

            avg_velocity = sum(velocity_pct) / len(velocity_pct)

            avg_shipping = (
                sum(shipping_delay_pct) /
                len(shipping_delay_pct)
            )

            avg_congestion = (
                sum(congestion_pct) /
                len(congestion_pct)
            )

            avg_logistics = (
                sum(logistics_stress_pct) /
                len(logistics_stress_pct)
            )

        else:

            avg_velocity = velocity_pct

            avg_shipping = shipping_delay_pct

            avg_congestion = congestion_pct

            avg_logistics = logistics_stress_pct

        # -----------------------------------
        # Prompt
        # -----------------------------------

        prompt = f"""
You are an operations forecasting analyst for a warehouse workforce planning system.

Your role is to explain workforce planning results clearly to warehouse leadership.

You MUST only use the supplied metrics.
Do NOT invent operational causes, percentages, or assumptions.

FORECAST METRICS

- Peak forecast week: Week {peak_week}
- Peak workload index: {peak:,.0f}
- Average workload index: {avg:,.0f}
- Demand classification: {demand_band}
- Labor cost classification: {cost_band}
- Projected labor cost impact: ${total_cost:,.0f}
- Recommended staffing action: {action}

OPERATIONAL STRESS METRICS

- Operational stress level: {stress_band}
- Demand velocity pressure: {avg_velocity:.1f}%
- Shipping delay pressure: {avg_shipping:.1f}%
- Warehouse congestion pressure: {avg_congestion:.1f}%
- Logistics stress pressure: {avg_logistics:.1f}%

FORECAST INTELLIGENCE METRICS

- Forecast trend direction: {trend_direction}
- Forecast volatility level: {volatility_band}
- Maximum consecutive VET weeks: {max_vet_streak}
- Maximum consecutive VTO weeks: {max_vto_streak}

RESPONSE REQUIREMENTS

1. Write exactly 5 concise executive sentences.
2. Use professional warehouse operations language.
3. Refer to demand as forecast demand or workload.
4. Do NOT mention AI, algorithms, models, or predictions.
5. If operational stress is High, mention coordination pressure and workload balancing carefully.
6. If action is VET:
   recommend targeted overtime planning before peak workload periods.
7. If action is VTO:
   recommend cautious labor reduction to avoid operational instability.
8. If action is NORMAL:
   recommend maintaining staffing levels with continued monitoring.
9. Mention labor cost discipline if labor cost classification is High.
10. Keep the tone operational, realistic, and concise.
"""

        completion = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:

        return f"Groq unavailable: {str(e)}"

# ----------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------

def display_ai_summary_with_note(ai_summary, status="success"):
    """
    Display the AI summary separately from the guardrail note
    so the disclaimer appears in a different color.
    """

    note_marker = "Note:"

    if note_marker in ai_summary:
        main_text, note_text = ai_summary.split(note_marker, 1)
        main_text = main_text.strip()
        note_text = note_marker + note_text.strip()
    else:
        main_text = ai_summary.strip()
        note_text = None

    if status == "warning":
        st.warning(main_text)
    else:
        st.success(main_text)

    if note_text:
        st.info(note_text)


def classify_demand_band(result_df):
    peak = result_df["predicted_demand"].max()
    avg = result_df["predicted_demand"].mean()
    recent = result_df["predicted_demand"].tail(4).mean()

    score = (peak * 0.25) + (avg * 0.45) + (recent * 0.30)

    q75 = result_df["predicted_demand"].quantile(0.75)
    q25 = result_df["predicted_demand"].quantile(0.25)

    if score >= q75:
        return "High"
    elif score <= q25:
        return "Low"
    else:
        return "Normal"


def classify_stress_band(v, s, c, l):
    vals = [v, s, c, l]

    if isinstance(v, list):
        vals = v + s + c + l

    score = max(vals)

    if score >= 20:
        return "High"
    elif score >= 8:
        return "Medium"
    else:
        return "Low"


def classify_cost_band(result_df):
    total_cost = result_df["estimated_cost"].sum()

    if total_cost >= 25000:
        return "High"
    elif total_cost >= 10000:
        return "Medium"
    else:
        return "Low"


def get_scenario_row(demand_band, stress_band, cost_band):
    row = scenario_df[
        (scenario_df["demand_band"] == demand_band) &
        (scenario_df["stress_band"] == stress_band) &
        (scenario_df["cost_band"] == cost_band)
    ]

    if len(row) == 0:
        return None

    return row.iloc[0]


# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
st.sidebar.header("Scenario Inputs")

# ----------------------------------------------------------
# SECTION 1 - FORECAST SETUP
# ----------------------------------------------------------
st.sidebar.subheader("📅 Forecast Setup")

# Weeks
weeks = st.sidebar.slider("Forecast Horizon (Weeks)", 1, 43, 12)

# Input Mode
mode = st.sidebar.radio(
    "Input Mode",
    ["Simple Scenario", "Advanced Weekly Table"]
)

st.sidebar.markdown("---")

# ------------------------------------------------
# CONDITIONAL FIELDS
# ------------------------------------------------
if mode == "Simple Scenario":

    scenario_name = st.sidebar.text_input(
        "Scenario Name",
        value="Standard Forecast"
    )

    request_id = st.sidebar.text_input(
        "Request ID",
        value="REQ001"
    )

else:

    scenario_name = st.sidebar.text_input(
        "Scenario Name",
        value="Advanced Scenario"
    )

    request_id = st.sidebar.text_input(
        "Request ID",
        value="REQ002"
    )
# ----------------------------------------------------------
# SECTION 2 - LABOR PLANNING SETTINGS
# ----------------------------------------------------------

st.sidebar.subheader("👷 Labor Planning")

workers_per_unit = st.sidebar.number_input(
    "Units per Worker Capacity",
    value=5000,
    help="Estimated workload handled per worker"
)

overtime_labor_cost_per_worker = st.sidebar.number_input(
    "Overtime Cost per Hour ($)",
    value=30,
    help="Estimated overtime labor rate"
)

hourly_labor_cost_per_worker = st.sidebar.number_input(
    "Regular Labor Cost per Hour ($)",
    value=20,
    help="Standard hourly labor cost"
)

st.sidebar.markdown("---")

# ----------------------------------------------------------
# SIMPLE MODE
# ----------------------------------------------------------
if mode == "Simple Scenario":

    # ----------------------------------------------------------
    # SECTION 3 - ECONOMIC DRIVERS
    # ----------------------------------------------------------
    st.sidebar.subheader("📈 Economic Drivers")

    temperature = st.sidebar.number_input(
        "Temperature",
        value=45.0
    )

    fuel_price = st.sidebar.number_input(
        "Fuel Price",
        value=3.20
    )

    cpi = st.sidebar.number_input(
        "CPI Index",
        value=225.0
    )

    unemployment = st.sidebar.number_input(
        "Unemployment Rate (%)",
        value=6.50
    )

    holiday = st.sidebar.selectbox(
        "Holiday Demand Week",
        [0, 1]
    )

    st.sidebar.markdown("---")

    # ----------------------------------------------------------
    # SECTION 4 - OPERATIONAL STRESS CONTROLS
    # ----------------------------------------------------------
    with st.sidebar.expander("⚙️ Advanced Scenario Stress Testing"):

        velocity_pct = st.slider(
            "Demand Velocity (%)",
            -20, 20, 0
        )

        shipping_delay_pct = st.slider(
            "Shipping Delay (%)",
            0, 30, 0
        )

        congestion_pct = st.slider(
            "Warehouse Congestion (%)",
            0, 30, 0
        )

        logistics_stress_pct = st.slider(
            "Logistics Stress (%)",
            0, 30, 0
        )
        st.sidebar.markdown("---")

    payload = {
        "mode": "simple",

        "request_id": request_id,
        "scenario_name": scenario_name,
        "weeks": weeks,
        "inputs": {
            "temperature": [temperature] * weeks,
            "fuel_price": [fuel_price] * weeks,
            "cpi": [cpi] * weeks,
            "unemployment": [unemployment] * weeks,
            "isholiday": [holiday] * weeks
        },
        "settings": {
            "workers_per_unit": workers_per_unit,
            "overtime_labor_cost_per_worker": overtime_labor_cost_per_worker,
            "hourly_labor_cost_per_worker": hourly_labor_cost_per_worker,
            "velocity_pct": velocity_pct,
            "shipping_delay_pct": shipping_delay_pct,
            "congestion_pct": congestion_pct,
            "logistics_stress_pct": logistics_stress_pct
        }
    }

# ----------------------------------------------------------
# ADVANCED MODE
# ----------------------------------------------------------
else:

    with st.sidebar.expander("⚙️ Advanced Scenario Stress Testing"):

        velocity_pct = st.slider(
            "Demand Velocity (%)",
            -20, 20, 0
        )

        shipping_delay_pct = st.slider(
            "Shipping Delay (%)",
            0, 30, 0
        )

        congestion_pct = st.slider(
            "Warehouse Congestion (%)",
            0, 30, 0
        )

        logistics_stress_pct = st.slider(
            "Logistics Stress (%)",
            0, 30, 0
        )

    st.subheader("Advanced Weekly Scenario Table")

    default_df = pd.DataFrame({
        "week": range(1, weeks + 1),

        "temperature": [45.0] * weeks,
        "fuel_price": [3.2] * weeks,
        "cpi": [225.0] * weeks,
        "unemployment": [6.5] * weeks,
        "isholiday": [0] * weeks,

        "velocity_pct": [velocity_pct] * weeks,
        "shipping_delay_pct": [shipping_delay_pct] * weeks,
        "congestion_pct": [congestion_pct] * weeks,
        "logistics_stress_pct": [logistics_stress_pct] * weeks
    })

    edited_df = st.data_editor(
        default_df,
        use_container_width=True,
        num_rows="fixed"
    )

    payload = {
        "mode": "advanced",

        "request_id": request_id,
        "scenario_name": scenario_name,
        "weeks": weeks,
        "inputs": {
            "temperature": edited_df["temperature"].tolist(),
            "fuel_price": edited_df["fuel_price"].tolist(),
            "cpi": edited_df["cpi"].tolist(),
            "unemployment": edited_df["unemployment"].tolist(),
            "isholiday": edited_df["isholiday"].tolist()
        },
        "settings": {
            "workers_per_unit": workers_per_unit,
            "overtime_labor_cost_per_worker": overtime_labor_cost_per_worker,
            "hourly_labor_cost_per_worker": hourly_labor_cost_per_worker,
            "velocity_pct": edited_df["velocity_pct"].tolist(),
            "shipping_delay_pct": edited_df["shipping_delay_pct"].tolist(),
            "congestion_pct": edited_df["congestion_pct"].tolist(),
            "logistics_stress_pct": edited_df["logistics_stress_pct"].tolist()
        }
    }
    
# -----------------------------------------
# OPERATIONAL CONFIDENCE SCORE
# -----------------------------------------

confidence = 100

# Demand volatility impact
confidence -= abs(velocity_pct) * 0.8

# Shipping delays hurt confidence
confidence -= shipping_delay_pct * 1.2

# Congestion hurts operations heavily
confidence -= congestion_pct * 1.5

# Logistics stress impact
confidence -= logistics_stress_pct * 1.3

# Clamp between 40 and 100
confidence = max(40, min(100, confidence))

if confidence >= 85:
    confidence_status = "High"

elif confidence >= 70:
    confidence_status = "Moderate"

else:
    confidence_status = "Low"

# -----------------------------------------
# PRIMARY RISK DRIVER
# -----------------------------------------

risk_map = {
    "Demand Velocity": abs(velocity_pct),
    "Shipping Delay": shipping_delay_pct,
    "Warehouse Congestion": congestion_pct,
    "Logistics Stress": logistics_stress_pct
}

primary_risk = max(risk_map, key=risk_map.get)

primary_risk_value = risk_map[primary_risk]

# ----------------------------------------------------------
# RUN BUTTON
# ----------------------------------------------------------
run_clicked = st.sidebar.button("🚀 Run Forecast")

if run_clicked:
    
    validation = validate_forecast_payload(payload)
    if not validation["valid"]:
        st.error("Forecast input failed guardrail validation.")
        unique_errors = list(dict.fromkeys(validation["errors"]))
        for error in unique_errors:
            st.warning(error)

        st.info(
            "Please correct the scenario input values in the sidebar, then run the forecast again."
        )
        
        st.stop() 
    
    safe_payload = validation["safe_payload"]
    
    try:
        # IMPORTANT:
        # Local:
        api_url = "http://localhost:5000/forecast"
        #
        # Docker:
        # api_url = "https://warehouse-backend-n7on.onrender.com/forecast"

        response = requests.post(api_url, json=safe_payload)

        if response.status_code == 200:
            st.success("Forecast Completed")
        else:
            st.text(response.text[:1000])
            st.error("Backend returned an error.")
            st.stop()

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to Flask API: {str(e)}")
        st.stop()

    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.stop()

    # ------------------------------------------------------
    # BLOCK 2 - DISPLAY SAVED RESULTS
    # ------------------------------------------------------
    data = response.json()

    # --------------------------------------------------
    # Executive Summary
    # --------------------------------------------------
    st.subheader("Executive Summary")

    col1, col2, col3, col4, col5, col6 = st.columns([0.7, 0.7, 0.7, 1.3, 0.7, 1.9])
    
    col1.metric("VET Weeks", data["summary"]["vet_weeks"])
    col2.metric("VTO Weeks", data["summary"]["vto_weeks"])
    col3.metric("Peak Week", data["summary"]["peak_demand_week"])
    
    col4.metric(
        "Total Cost",
        f'${data["summary"]["total_cost"]:,.0f}'
    )
    
    with col5:
        st.metric(
            "Confidence",
            f"{confidence:.0f}%"
        )
    
    
    with col6:
        st.metric(
            "Primary Risk Driver",
            primary_risk
        )
    
    st.caption(
        f"Primary Risk Driver: {primary_risk} | Risk Pressure: {primary_risk_value:.1f}%"
    )

    # --------------------------------------------------
    # Output Table
    # --------------------------------------------------
    st.subheader("Forecast Output")

    result_df = pd.DataFrame(data["forecast"])

    forecast_rows = result_df.to_dict(orient="records")

    decision_validation = validate_staffing_decisions(forecast_rows)
    
    if not decision_validation["valid"]:
        st.error("Forecast output failed guardrail validation.")
        for error in decision_validation["errors"]:
            st.warning(error)
        st.stop()

    common_layout = dict(
        height=260,
        margin=dict(l=20, r=20, t=45, b=20),
        title_x=0.0
    )

    # Demand Forecast Chart
    fig1 = px.line(
        result_df,
        x="week",
        y="predicted_demand",
        markers=True,
        title=f"{weeks} Week Demand Forecast"
    )

    # Cost Chart
    fig2 = px.bar(
        result_df,
        x="week",
        y="estimated_cost",
        color="decision",
        title="Weekly Labor Cost"
    )

    fig1.update_layout(**common_layout)
    fig2.update_layout(**common_layout)

    # Cumulative Cost Chart
    fig3 = px.line(
        result_df,
        x="week",
        y="cumulative_future_cost",
        markers=True,
        title="Cumulative Future Cost"
    )

    fig3.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=35, b=10)
    )

    # ==================================
    # LAYOUT
    # ==================================
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    colA, colB, colC = st.columns([1, 2, 1])

    with colB:
        st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Detailed Forecast Table"):
        styled_df = result_df.style.format({
            "week": "{:.0f}",
            "predicted_demand": "{:,.0f}",
            "estimated_cost": "${:,.0f}",
            "cumulative_future_cost": "${:,.0f}",
            "extra_workers_needed": "{:.0f}",
            "workers_to_reduce": "{:.0f}"
        }).set_properties(
            subset=[
                "predicted_demand",
                "estimated_cost",
                "cumulative_future_cost",
                "extra_workers_needed",
                "workers_to_reduce"
            ],
            **{"text-align": "right"}
        ).set_properties(
            subset=["week", "decision"],
            **{"text-align": "center"}
        ).apply(
            lambda row: [
                (
                    "background-color:#145a32;"
                    "color:white;"
                    "font-weight:bold;"
                    "text-align:center;"
                    "border-radius:4px;"
                    if (col == "decision" and row["decision"] == "VET")
                    else
                    "background-color:#7d5a00;"
                    "color:white;"
                    "font-weight:bold;"
                    "text-align:center;"
                    "border-radius:4px;"
                    if (col == "decision" and row["decision"] == "VTO")
                    else
                    "background-color:#444444;"
                    "color:white;"
                    "font-weight:bold;"
                    "text-align:center;"
                    "border-radius:4px;"
                    if (col == "decision" and row["decision"] == "NORMAL")
                    else ""
                )
                for col in row.index
            ],
            axis=1
        ).set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#111111"),
                    ("color", "white"),
                    ("font-weight", "bold"),
                    ("text-align", "center")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("border", "1px solid #333333"),
                    ("padding", "6px")
                ]
            }
        ])

        st.dataframe(
            styled_df,
            use_container_width=True,
            height=420
        )

    st.caption(
        "Public Walmart weekly sales data is used as a proxy for operational demand. "
        "Staffing outputs are scenario-based estimates using configurable capacity assumptions."
    )
    # ------------------------------------------------------
    # RECOMMENDATIONS (SMART SCENARIO ENGINE)
    # ------------------------------------------------------
    st.subheader("Operational Recommendations")

    # classify demand from forecast results
    demand_band = classify_demand_band(result_df)

    # classify stress depending on mode
    if mode == "Simple Scenario":
        stress_band = classify_stress_band(
            velocity_pct,
            shipping_delay_pct,
            congestion_pct,
            logistics_stress_pct
        )
    else:
        stress_band = classify_stress_band(
            edited_df["velocity_pct"].tolist(),
            edited_df["shipping_delay_pct"].tolist(),
            edited_df["congestion_pct"].tolist(),
            edited_df["logistics_stress_pct"].tolist()
        )

    # classify cost
    cost_band = classify_cost_band(result_df)

    # lookup row from CSV
    rec = get_scenario_row(
        demand_band,
        stress_band,
        cost_band
    )

    if rec is None:
        st.warning(
            "No matching scenario rule was found for this Demand/Stress/Cost combination."
        )
        st.stop()

    risk_values = {
        "Demand Velocity": abs(velocity_pct),
        "Shipping Delay": abs(shipping_delay_pct),
        "Warehouse Congestion": abs(congestion_pct),
        "Logistics Stress": abs(logistics_stress_pct)
    }

    primary_risk_driver = max(risk_values, key=risk_values.get)
    primary_risk_value = risk_values[primary_risk_driver]

    # Detect low-risk scenarios
    if primary_risk_value < 5:
        primary_risk_display = "Minimal Operational Risk"
    else:
        primary_risk_display = f"{primary_risk_driver} ({primary_risk_value:.1f}%)"
        
    # ------------------------------------------------------
    # ALIGN FINAL ACTION WITH WEEKLY FORECAST
    # ------------------------------------------------------

    vet_weeks = (
        result_df["decision"] == "VET"
    ).sum()

    vto_weeks = (
        result_df["decision"] == "VTO"
    ).sum()

    normal_weeks = (
        result_df["decision"] == "NORMAL"
    ).sum()

    # Majority VET weeks
    if vet_weeks >= (weeks * 0.6):

        rec["action"] = "VET"

        rec["severity"] = "Critical"

        rec["short_message"] = (
            "Sustained elevated workload detected across forecast horizon."
        )

        rec["final_recommendation"] = (
            "Maintain proactive overtime staffing plans "
            "to support forecast workload requirements."
        )

        rec["long_narrative"] = (
            "The forecast indicates sustained elevated workload "
            "conditions across the planning horizon. "
            "Operational planning should prioritize proactive "
            "overtime scheduling and workforce coordination "
            "to maintain throughput stability and reduce backlog risk."
        )

    # Majority VTO weeks
    elif vto_weeks >= (weeks * 0.6):

        rec["action"] = "VTO"

        rec["severity"] = "Warning"

        rec["short_message"] = (
            "Sustained excess labor capacity detected."
        )

        rec["final_recommendation"] = (
            "Use selective VTO and tighter labor scheduling "
            "to reduce excess labor costs."
        )

        rec["long_narrative"] = (
            "The forecast indicates sustained periods of excess "
            "labor capacity across the planning horizon. "
            "Operations leadership should consider selective "
            "VTO strategies and tighter scheduling discipline "
            "to control labor costs while maintaining staffing flexibility."
        )

    elif vet_weeks > 0 and vto_weeks > 0:

        rec["action"] = "MIXED"
    
        rec["severity"] = "Info"
    
        rec["short_message"] = (
            "Mixed staffing pattern detected with both VET and VTO weeks."
        )
    
        rec["final_recommendation"] = (
            "Maintain baseline staffing while preparing targeted VET coverage "
            "for high-demand weeks and selective VTO for low-demand weeks."
        )
    
        rec["long_narrative"] = (
            "The forecast indicates a mixed staffing pattern across the planning horizon. "
            "Operations leadership should maintain baseline staffing, prepare targeted "
            "VET coverage during high-demand weeks, and consider selective VTO during "
            "lower-demand weeks to balance labor availability and cost control."
        )

    # Majority NORMAL weeks
    else:

        rec["action"] = "NORMAL"

        rec["severity"] = "Info"

        rec["short_message"] = (
            "Forecast workload remains operationally stable."
        )

        rec["final_recommendation"] = (
            "Maintain current staffing strategy with continued monitoring."
        )

        rec["long_narrative"] = (
            "The forecast indicates relatively balanced workload "
            "conditions across the planning horizon. "
            "Current staffing levels appear sufficient, "
            "though operational monitoring should continue "
            "to identify emerging workload changes."
        )

    # ------------------------------------------------------
    # SHOW SCENARIO SUMMARY
    # ------------------------------------------------------

    # show scenario summary
    st.write(
        f"Scenario: Demand={demand_band} | Stress={stress_band} | Cost={cost_band}"
    )

    if rec is not None:
        action = rec["action"]
        severity = rec["severity"]

        # Card 1 Demand Alert
        if severity == "Critical":
            st.error("🔥 " + rec["short_message"])
        elif severity == "Warning":
            st.warning("⚠️ " + rec["short_message"])
        else:
            st.info("📊 " + rec["short_message"])

        # Card 2 Operational Guidance
        st.info("📈 " + rec["final_recommendation"])

        # Card 3 Cost Insight
        total_cost = result_df["estimated_cost"].sum()
        st.info(f"💰 Projected total labor impact: ${total_cost:,.0f}")

        # Card 4 Action
        if action == "VET":
            st.success("✅ Recommended Action: Increase Staffing (VET)")
        elif action == "VTO":
            st.warning("💤 Recommended Action: Offer Voluntary Time Off (VTO)")
        elif action == "MIXED":
            st.info("🔄 Recommended Action: Mixed Staffing Plan")
        else:
            if vet_weeks > 0 and vto_weeks == 0:
                st.info("🟦 Recommended Action: Maintain Baseline Staffing + Targeted VET Coverage")
            elif vto_weeks > 0 and vet_weeks == 0:
                st.info("🟦 Recommended Action: Maintain Baseline Staffing + Selective VTO")
            elif vet_weeks > 0 and vto_weeks > 0:
                st.info("🔄 Recommended Action: Maintain Baseline Staffing + Mixed VET/VTO Plan")
            else:
                st.info("🟦 Recommended Action: Maintain Current Staffing")

        # Card 5 Peak Week Alert
        peak_row = result_df.loc[result_df["predicted_demand"].idxmax()]
        peak_week = int(peak_row["week"])

        st.error(f"🔥 Highest demand expected in Week {peak_week}. Prepare early.")

        # Rule Engine Explanation
        with st.expander("### Rule Engine Interpretation"):
            st.info(rec["long_narrative"].replace(". ", ".\n\n"))

        st.warning(
            f"Primary Operational Risk Driver: {primary_risk_display}"
        )

        # -----------------------------------
        # GEMINI HEADER
        # -----------------------------------
        title_col, btn_col, count_col = st.columns([8, 0.7, 1])

        with title_col:
            st.markdown("### AI Operational Decision Summary")

        st.info(
            "This AI summary is a decision-support explanation only. "
            "It does not override the forecast model, business rules, or human operations judgment."
        )

        # first load or retry
        with st.spinner("Running Multi-Agent Intelligence.."):
                #ai_summary = get_gemini_explanation(result_df, rec)
                # ai_summary = get_gemini_explanation(
                #     result_df,
                #     rec,
                #     stress_band,
                #     velocity_pct if mode == "Simple Scenario" else edited_df["velocity_pct"].tolist(),
                #     shipping_delay_pct if mode == "Simple Scenario" else edited_df["shipping_delay_pct"].tolist(),
                #     congestion_pct if mode == "Simple Scenario" else edited_df["congestion_pct"].tolist(),
                #     logistics_stress_pct if mode == "Simple Scenario" else edited_df["logistics_stress_pct"].tolist()
                # )
                peak_week = result_df.loc[
                    result_df["predicted_demand"].idxmax(),
                    "week"
                ]

                ai_result = run_operational_crew(
                    result_df,
                    stress_band,
                    total_cost,
                    peak_week,
                    confidence,
                    primary_risk_display,
                    vet_weeks,
                    vto_weeks
                )
                
                ai_summary = ai_result["summary"]
                operational_state = ai_result["state"]

        if "unavailable" in ai_summary.lower() or "busy" in ai_summary.lower():
            #ai_summary = get_groq_explanation(result_df, rec)
            ai_summary = get_groq_explanation(
                result_df,
                rec,
                stress_band,
                velocity_pct if mode == "Simple Scenario" else edited_df["velocity_pct"].tolist(),
                shipping_delay_pct if mode == "Simple Scenario" else edited_df["shipping_delay_pct"].tolist(),
                congestion_pct if mode == "Simple Scenario" else edited_df["congestion_pct"].tolist(),
                logistics_stress_pct if mode == "Simple Scenario" else edited_df["logistics_stress_pct"].tolist()
            )
            ai_summary = ai_summary.replace(". ", ".\n\n")
            ai_summary = constrain_ai_summary(
                ai_text=ai_summary,
                allowed_decisions=["VET", "VTO", "NORMAL", "MIXED"],
                max_words=180
            )
            
            display_ai_summary_with_note(ai_summary, status="success")
            
        else:
            ai_summary = ai_summary.replace(". ", ".\n\n")
            ai_summary = constrain_ai_summary(
                ai_text=ai_summary,
                allowed_decisions=["VET", "VTO", "NORMAL", "MIXED"],
                max_words=180
            )
            display_ai_summary_with_note(ai_summary, status="success")

        st.subheader("AI Decision Workflow Architecture")
        
        st.info(
            "Autonomous workflow active: Forecast Node -> Staffing Node -> Risk Node -> "
            "Cost Node -> RAG Context Node -> Executive Summary Node -> Operational Memory "
            "-> Autonomous Supervisor -> Final Recommendation + Trace"
        )
        
    else:
        st.info("No scenario matched.")

        
    # ------------------------------------------------------
    # AUTONOMOUS SUPERVISOR OUTPUT
    # ------------------------------------------------------
    st.subheader("Autonomous Control Layer")

    final_recommendation = getattr(operational_state, "final_recommendation", "")
    guardrail_status = getattr(operational_state, "guardrail_status", "")
    risk_level = getattr(operational_state, "risk_level", "")
    autonomous_summary = getattr(operational_state, "autonomous_summary", "")
    trace = getattr(operational_state, "trace", [])

    if final_recommendation or guardrail_status or risk_level or autonomous_summary:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Final Recommendation", final_recommendation or "N/A")

        with col2:
            st.metric("Guardrail Status", guardrail_status.title() or "N/A")

        with col3:
            st.metric("Risk Level", risk_level or "N/A")

        if autonomous_summary:
            st.info(autonomous_summary)

        with st.expander("Autonomous Agent Trace", expanded=False):
            if trace:
                for step in trace:
                    st.write(f"- {step}")
            else:
                st.write("No autonomous trace returned.")

    else:
        st.warning("Autonomous supervisor output was not returned.")
        
    # ------------------------------------------------------
    # Operational State Trace
    # ------------------------------------------------------

    with st.expander("🧠 Operational State Trace", expanded=False):

        st.write("This section shows the shared operational state passed through the node workflow.")

        st.markdown("### RAG Context Node Output")

        st.text(getattr(operational_state, "rag_context", ""))

        st.markdown("### Node Workflow")

        st.code(
            "Forecast Metrics → OperationalState → Forecast Node → Staffing Node → Cost Node → Executive Summary Node → Memory Store",
            language="text"
        )
    
        st.markdown("### Current Forecast State")
    
        st.write({
            "Peak Week": operational_state.peak_week,
            "Stress Band": operational_state.stress_band,
            "Confidence Score": operational_state.confidence_score,
            "Primary Risk Driver": operational_state.primary_risk_display,
            "VET Weeks": operational_state.vet_weeks,
            "VTO Weeks": operational_state.vto_weeks,
        })

        st.markdown("### Forecast Node Output")

        st.json({
            "forecast_summary": getattr(operational_state, "forecast_summary", ""),
            "forecast_risk_signal": getattr(operational_state, "forecast_risk_signal", ""),
            "forecast_confidence": getattr(operational_state, "forecast_confidence", "")
        })
        
        st.markdown("### Staffing Node Output")
        
        st.json({
            "staffing_summary": getattr(operational_state, "staffing_summary", ""),
            "staffing_action": getattr(operational_state, "staffing_action", ""),
            "staffing_risk_level": getattr(operational_state, "staffing_risk_level", ""),
            "operational_concern": getattr(operational_state, "operational_concern", ""),
            "operational_reason": getattr(operational_state, "operational_reason", ""),
            "workforce_recommendation": getattr(operational_state, "workforce_recommendation", "")
        })

        st.markdown("### Cost Node Output")

        st.json({
            "cost_summary": getattr(operational_state, "cost_summary", ""),
            "cost_results": getattr(operational_state, "cost_results", {})
        })
        
        st.markdown("### Executive Node Output")
        
        st.json({
            "executive_summary": getattr(operational_state, "executive_summary", "")
        })
    
        st.markdown("### Memory Context Used")
    
        st.text(operational_state.memory_context or "No historical memory used for this run.")
    
        st.markdown("### Executive Node Output")
    
        st.text(operational_state.executive_summary)
    
    # ------------------------------------------------------
    # RAW JSON (OPTIONAL)
    # ------------------------------------------------------
    with st.expander("View Raw JSON Response"):
        st.json(data)

