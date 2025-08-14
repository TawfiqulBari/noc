from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import uvicorn
import os
from datetime import datetime, timedelta
from influxdb_client import Point
from typing import List, Dict

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://noc.tawfiqulbari.work"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize InfluxDB client
influxdb = InfluxDBClient(
    url=os.getenv("INFLUXDB_URL", "http://influxdb:8086"),
    token=os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token"),
    org=os.getenv("INFLUXDB_ORG", "monitoring")
)
write_api = influxdb.write_api(write_options=SYNCHRONOUS)
query_api = influxdb.query_api()

@app.get("/")
async def root():
    return {"message": "Monitoring API is running"}

@app.get("/metrics")
async def get_metrics():
    """Get recent metrics from InfluxDB"""
    query = f'''
    from(bucket: "metrics")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "system_metrics")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    result = query_api.query(query)
    
    metrics = {
        "cpu": [],
        "memory": [],
        "containers": []
    }
    
    for table in result:
        for record in table.records:
            metrics["cpu"].append({
                "timestamp": record.get_time().isoformat(),
                "value": record.values.get("cpu_usage")
            })
            metrics["memory"].append({
                "timestamp": record.get_time().isoformat(),
                "value": record.values.get("memory_usage")
            })
            metrics["containers"].append({
                "timestamp": record.get_time().isoformat(),
                "value": record.values.get("container_count")
            })
    
    return metrics

@app.get("/alerts")
async def get_alerts():
    """Get recent alerts from InfluxDB"""
    query = f'''
    from(bucket: "metrics")
      |> range(start: -24h)
      |> filter(fn: (r) => r._measurement == "alerts")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    result = query_api.query(query)
    
    alerts = []
    for table in result:
        for record in table.records:
            alerts.append({
                "severity": record.values.get("severity"),
                "message": record.values.get("message"),
                "timestamp": record.get_time().isoformat(),
                "status": record.values.get("status")
            })
    
    return alerts

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)