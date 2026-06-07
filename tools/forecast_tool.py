import requests

def run_forecast_tool(payload):

    response = requests.post(
        "http://127.0.0.1:5000/forecast",
        json=payload
    )

    return response.json()