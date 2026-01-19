import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Load telemetry data from JSON
df = pd.read_json("q-vercel-latency.json")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class TelemetryRequest(BaseModel):
    regions: List[str]
    threshold_ms: int



@app.post("/")
def get_metrics(request: TelemetryRequest):
    results = {}
    for region in request.regions:
        region_df = df[df["region"] == region]
        if not region_df.empty:
            avg_latency = region_df["latency_ms"].mean()
            p95_latency = region_df["latency_ms"].quantile(0.95)
            avg_uptime = region_df["uptime_pct"].mean()
            breaches = (region_df["latency_ms"] > request.threshold_ms).sum()

            results[region] = {
                "avg_latency": round(avg_latency, 2),
                "p95_latency": round(p95_latency, 2),
                "avg_uptime": round(avg_uptime, 4),
                "breaches": int(breaches),
            }
        else:
            results[region] = {}
    return {"regions":results}