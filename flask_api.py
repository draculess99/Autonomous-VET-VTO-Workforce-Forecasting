#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ===============================================
# Flask API for the XGBoost Forecaster
# Walmart / VET / VTO Forecast Deployment
# bash: python VET_VTO_Forecaster.py
# bash: http://127.0.0.1:5000 
# ===============================================


# # Run Flask App
# 
# ```bash
# python app.py
# ```
# 
# Open in browser:
# 
# ```text
# http://127.0.0.1:5000
# ```
# 
# ---
# 
# # Example JSON Input (Postman / CURL)
# 
# ```json
# {
#   "request_id": "forecast_001",
#   "scenario_name": "Spring Holiday Plan",
#   "weeks": 12,
#   "inputs": {
#       "temperature": [42,44,40,38,39,41,45,47,50,51,52,55],
#       "fuel_price": [3.2,3.2,3.2,3.1,3.1,3.1,3.0,3.0,3.1,3.2,3.3,3.4],
#       "cpi": [220,220,221,221,222,222,223,223,224,224,225,225],
#       "unemployment": [7.1,7.0,7.0,7.0,6.9,6.9,6.8,6.8,6.7,6.7,6.6,6.5],
#       "isholiday": [0,0,0,0,0,0,0,0,0,0,1,0]
#   },
#   "settings": {
#     "labor_cost_per_worker": 5000,
#     "overtime_wage": 30,
#     "hourly_wage": 29
#   }
# }
# ```
# 
# ---
# 
# # Example JSON Output
# 
# ```json
# {
# {
#     "forecast": [
#         {
#             "cumulative_future_cost": 0,
#             "decision": "NORMAL",
#             "estimated_cost": 0,
#             "extra_workers_needed": 0,
#             "predicted_demand": 47130076.0,
#             "week": 1,
#             "workers_to_reduce": 0
#         },
#         {
#             "cumulative_future_cost": 1170,
#             "decision": "VET",
#             "estimated_cost": 1170,
#             "extra_workers_needed": 39,
#             "predicted_demand": 47866028.0,
#             "week": 2,
#             "workers_to_reduce": 0
#         },
#         {
#             "cumulative_future_cost": 11760,
#             "decision": "VET",
#             "estimated_cost": 10590,
#             "extra_workers_needed": 353,
#             "predicted_demand": 49433788.0,
#             "week": 3,
#             "workers_to_reduce": 0 
#     ...
#     ...
#         {
#             "cumulative_future_cost": 19200,
#             "decision": "NORMAL",
#             "estimated_cost": 0,
#             "extra_workers_needed": 0,
#             "predicted_demand": 46295492.0,
#             "week": 12,
#             "workers_to_reduce": 0
#         }
#     ],
#     "inputs_used": {
#         "cpi": {
#             "avg": 222.5,
#             "default_used": true,
#             "length": 12,
#             "max": 225,
#             "min": 220,
#             "values": "220, 220, 221, 221, 222, 222, 223, 223, 224, 224, 225, 225"
#     ...
#     ...
#         "unemployment": {
#             "avg": 6.83,
#             "default_used": true,
#             "length": 12,
#             "max": 7.1,
#             "min": 6.5,
#             "values": "7.1, 7.0, 7.0, 7.0, 6.9, 6.9, 6.8, 6.8, 6.7, 6.7, 6.6, 6.5"
#         },
#         "weeks": 12
#     },
#     "recommendations": [
#         "Increase staffing during 3 week(s) of forecasted high demand.",
#         "Highest demand expected in Week 3. Prepare staffing early.",
#         "Large labor requirement detected. Consider temporary staffing support.",
#         "Projected added labor cost is $19200."
#     ],
#     "request_id": "forecast_001",
#     "scenario_name": "Spring Holiday Plan",
#     "status": "success",
#     "summary": {
#         "normal_weeks": 9,
#         "peak_demand_value": 49433788.0,
#         "peak_demand_week": 3,
#         "total_cost": 19200,
#         "total_extra_workers": 640,
#         "total_workers_reduced": 0,
#         "vet_weeks": 3,
#         "vto_weeks": 0,
#         "weeks_forecasted": 12
#     }
#   ]
# }
# ```

# In[ ]:


# !jupyter nbconvert --to script VET_VTO_Forecaster.ipynb


# In[ ]:


# pip install flask pandas joblib

from flask import Flask, request, jsonify
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)


# In[ ]:


# ---------------------------------------------------
# LOAD SAVED FORECASTER
# ---------------------------------------------------

bundle = joblib.load("models/warehouse_system.pkl")

forecaster = bundle["forecaster"]
vet_threshold = bundle["vet_threshold"]
vto_threshold = bundle["vto_threshold"]



# In[ ]:


# ---------------------------------------------------
# SETTINGS
# ---------------------------------------------------

DEFUALT_WORKERS_PER_UNIT = 5000        # demand per worker
DEFUALT_OVERTIME_LABOR_COST_PER_WORKER = 30     # optional amzn cost estimate
DEFUALT_HOURLY_LABOR_COST_PER_WORKER = 20     # optional amzn cost estimate
# ---------------------------------------------------
# ROOT TEST
# ---------------------------------------------------

@app.route("/")
def home():
    return {"message": "Warehouse Forecast API Running"}


# In[ ]:


# ---------------------------------------------------
# FORECAST ENDPOINT
# ---------------------------------------------------

@app.route("/forecast", methods=["POST"])
def forecast():

    data = request.json

    request_id = data.get("request_id", "forecast_default")
    scenario_name = data.get("scenario_name", "Standard Forecast")
    weeks = data.get("weeks", 43)

    # -----------------------------------
    # Defaults for Missing Inputs
    # -----------------------------------
    inputs = data.get("inputs", {})

    temperature = inputs.get("temperature", [45] * weeks)
    fuel_price = inputs.get("fuel_price", [3.2] * weeks)
    cpi = inputs.get("cpi", [225] * weeks)
    unemployment = inputs.get("unemployment", [6.5] * weeks)
    isholiday = inputs.get("isholiday", [0] * weeks)

    # temp_series = pd.Series(data["temperature"])
    temp_series = pd.Series(temperature)
    high_temp = temp_series.quantile(0.90)
    low_temp = temp_series.quantile(0.10)

    # -----------------------------------
    # Defaults for Missing settings
    # -----------------------------------
    settings = data.get("settings", {})

    WORKERS_PER_UNIT = settings.get("workers_per_unit", DEFUALT_WORKERS_PER_UNIT)
    OVERTIME_LABOR_COST_PER_WORKER = settings.get("overtime_labor_cost_per_worker", DEFUALT_OVERTIME_LABOR_COST_PER_WORKER)
    HOURLY_LABOR_COST_PER_WORKER = settings.get("hourly_labor_cost_per_worker", DEFUALT_HOURLY_LABOR_COST_PER_WORKER)


    # ======================================================
    # NEW SETTINGS FROM STREAMLIT  <<< ADD THIS BLOCK
    # ======================================================
    # velocity_pct = settings.get("velocity_pct", 0)
    # shipping_delay_pct = settings.get(
    #     "shipping_delay_pct",
    #     0
    # )

    # congestion_pct = settings.get(
    #     "congestion_pct",
    #     0
    # )

    # logistics_stress_pct = settings.get(
    #     "logistics_stress_pct",
    #     0
    # )
    mode = data.get("mode", "simple")

    velocity_pct = settings.get("velocity_pct", 0)
    shipping_delay_pct = settings.get("shipping_delay_pct", 0)
    congestion_pct = settings.get("congestion_pct", 0)
    logistics_stress_pct = settings.get("logistics_stress_pct", 0)

    def ensure_list(val, default=0):
        if isinstance(val, list):
            arr = val
        else:
            arr = [val] * weeks

        arr = list(arr)

        if len(arr) < weeks:
            arr += [default] * (weeks - len(arr))

        return arr[:weeks]

    velocity_pct = ensure_list(velocity_pct, 0)
    shipping_delay_pct = ensure_list(shipping_delay_pct, 0)
    congestion_pct = ensure_list(congestion_pct, 0)
    logistics_stress_pct = ensure_list(logistics_stress_pct, 0)

    # -----------------------------------
    # Ensure Correct Length
    # -----------------------------------

    def fix_length(arr, default_val):
        arr = list(arr)
        if len(arr) < weeks:
            arr += [default_val] * (weeks - len(arr))
        return arr[:weeks]


    temperature = fix_length(temperature, 45)
    fuel_price = fix_length(fuel_price, 3.2)
    cpi = fix_length(cpi, 225)
    unemployment = fix_length(unemployment, 6.5)
    isholiday = fix_length(isholiday, 0)

    # ----------------------------------
    # Build future_exog 
    # ----------------------------------

    # future_exog = pd.DataFrame({
    #     "IsHoliday": data["isholiday"][:weeks],
    #     "Temperature": data["temperature"][:weeks],
    #     "Fuel_Price": data["fuel_price"][:weeks],
    #     "CPI": data["cpi"][:weeks],
    #     "Unemployment": data["unemployment"][:weeks]
    # })

    future_exog = pd.DataFrame({
        "IsHoliday": isholiday[:weeks],
        "Temperature": temperature[:weeks],
        "Fuel_Price": fuel_price[:weeks],
        "CPI": cpi[:weeks],
        "Unemployment": unemployment[:weeks]
    })

    # OPTIONAL FEATURE ENGINEERING  <
    # ======================================================
    # future_exog["sales_velocity"] = velocity_pct / 100

    # future_exog["backlog_proxy"] = shipping_delay_pct / 100

    # future_exog["warehouse_congestion"] = congestion_pct / 100

    # future_exog["logistics_stress"] = (
    #     logistics_stress_pct / 100
    # )

    future_exog["sales_velocity"] = np.array(velocity_pct) / 100
    future_exog["backlog_proxy"] = np.array(shipping_delay_pct) / 100
    future_exog["warehouse_congestion"] = np.array(congestion_pct) / 100
    future_exog["logistics_stress"] = np.array(logistics_stress_pct) / 100

    # future_exog["sales_velocity"] = 0
    # future_exog["backlog_proxy"] = 0

    future_exog["extreme_temp"] = (
        (future_exog["Temperature"] > high_temp) |
        (future_exog["Temperature"] < low_temp)
    ).astype(int)

    # ----------------------------------
    # Datetime Index
    # ----------------------------------

    future_dates = pd.date_range(
        start=forecaster.last_window_.index[-1] + pd.Timedelta(weeks=1),
        periods=weeks,
        freq="W-FRI"
    )

    future_exog.index = future_dates

    # ----------------------------------
    # Predict
    # ----------------------------------

    pred = forecaster.predict(
        steps=weeks,
        exog=future_exog
    )

    # ======================================================
    # POST-FORECAST ADJUSTMENTS  <<< ADD THIS BLOCK
    # ======================================================

    # # Demand momentum raises/lowers demand
    # pred = pred * (1 + velocity_pct / 100)

    # # Shipping delays reduce sales fulfillment
    # pred = pred * (1 - shipping_delay_pct / 100)

    # # Congestion reduces warehouse throughput
    # pred = pred * (1 - congestion_pct / 100)

    # # Overall logistics stress
    # pred = pred * (1 - logistics_stress_pct / 100)

    pred = pred * (1 + np.array(velocity_pct) / 100)
    pred = pred * (1 - np.array(shipping_delay_pct) / 100)
    pred = pred * (1 - np.array(congestion_pct) / 100)
    pred = pred * (1 - np.array(logistics_stress_pct) / 100)

    # ------------------------------------------------------
    # CONTINUE YOUR EXISTING VET/VTO LOOP
    # ------------------------------------------------------
    output = []
    cumulative_cost = 0

    # ----------------------------------
    # Summary Counters
    # ----------------------------------

    vet_weeks = 0
    vto_weeks = 0
    normal_weeks = 0

    total_extra_workers = 0
    total_workers_reduced = 0

    peak_demand = 0
    peak_week = 0

    # ----------------------------------
    # Loop through predictions
    # ----------------------------------

    for i, value in enumerate(pred):

        if value >= vet_threshold:
            decision = "VET"
            extra_workers = int((value - vet_threshold) / WORKERS_PER_UNIT)
            reduce_workers = 0
            est_cost = extra_workers * OVERTIME_LABOR_COST_PER_WORKER
            vet_weeks += 1

        elif value <= vto_threshold:
            decision = "VTO"
            extra_workers = 0
            reduce_workers = int((vto_threshold - value) / WORKERS_PER_UNIT)
            est_cost = reduce_workers * HOURLY_LABOR_COST_PER_WORKER
            vto_weeks += 1

        else:
            decision = "NORMAL"
            extra_workers = 0
            reduce_workers = 0
            est_cost = 0
            normal_weeks += 1

        cumulative_cost += est_cost

        total_extra_workers += extra_workers
        total_workers_reduced += reduce_workers

        # Peak demand
        if value > peak_demand:
            peak_demand = float(value)
            peak_week = i + 1

        output.append({
            "week": i + 1,
            "predicted_demand": round(float(value), 2),
            "decision": decision,
            "extra_workers_needed": extra_workers,
            "workers_to_reduce": reduce_workers,
            "estimated_cost": est_cost,
            "cumulative_future_cost": cumulative_cost
        })

    # ----------------------------------
    # Create Summary
    # ----------------------------------

    summary = {
        "weeks_forecasted": weeks,
        "vet_weeks": vet_weeks,
        "vto_weeks": vto_weeks,
        "normal_weeks": normal_weeks,
        "total_extra_workers": total_extra_workers,
        "total_workers_reduced": total_workers_reduced,
        "total_cost": cumulative_cost,
        "peak_demand_week": peak_week,
        "peak_demand_value": peak_demand
    }

 # -----------------------------------
    # Return Inputs Used + Summary + Forecast
    # -----------------------------------

    def summarize_input(values, field_name, data):
        return {
            "default_used": field_name not in data,
            "length": len(values),
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values)/len(values), 2),
            "values": ", ".join(map(str, values))
        }

    inputs_used = {
        "weeks": weeks,
        "temperature": summarize_input(temperature, "temperature", data),
        "fuel_price": summarize_input(fuel_price, "fuel_price", data),
        "cpi": summarize_input(cpi, "cpi", data),
        "unemployment": summarize_input(unemployment, "unemployment", data),
        "isholiday": summarize_input(isholiday, "isholiday", data)
    }

    simulation_controls = {
        "mode": mode,
        "workers_per_unit": WORKERS_PER_UNIT,
        "overtime_labor_cost_per_worker": OVERTIME_LABOR_COST_PER_WORKER,
        "hourly_labor_cost_per_worker": HOURLY_LABOR_COST_PER_WORKER,
        "demand_velocity_pct": ", ".join(map(str, velocity_pct)),
        "shipping_delay_pct": ", ".join(map(str, shipping_delay_pct)),
        "warehouse_congestion_pct": ", ".join(map(str, congestion_pct)),
        "logistics_stress_pct": ", ".join(map(str, logistics_stress_pct))
    }
# ----------------------------------
# Recommendation Block
# ----------------------------------

    recommendations = []

    if vet_weeks > 0:
        recommendations.append(
            f"Increase staffing during {vet_weeks} week(s) of forecasted high demand."
        )

    if vto_weeks > 0:
        recommendations.append(
            f"Offer VTO during {vto_weeks} low-demand week(s) to reduce labor cost."
        )

    if peak_week > 0:
        recommendations.append(
            f"Highest demand expected in Week {peak_week}. Prepare staffing early."
        )

    if total_extra_workers > 50:
        recommendations.append(
            "Large labor requirement detected. Consider temporary staffing support."
        )

    if cumulative_cost > 0:
        recommendations.append(
            f"Projected added labor cost is ${round(cumulative_cost,2)}."
        )
    elif cumulative_cost < 0:
        recommendations.append(
            f"Projected labor savings is ${round(abs(cumulative_cost),2)}."
        )

    if len(recommendations) == 0:
        recommendations.append(
            "Demand stable. Maintain standard staffing plan."
        )

    return jsonify({
        "status": "success",
        "inputs_used": inputs_used,
        "simulation_controls": simulation_controls,
        "request_id": request_id,
        "scenario_name": scenario_name,
        "summary": summary,
        "forecast": output,
        "recommendations": recommendations
    })

# ---------------------------------------------------
# RUN
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

#if __name__ == "__main__": app.run(host="0.0.0.0", port=5000, debug=True)



# In[ ]:




