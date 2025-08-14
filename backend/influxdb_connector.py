from influxdb_client.client.write_api import SYNCHRONOUS
import os
from influxdb_client import InfluxDBClient

def init_influxdb():
    """Initialize InfluxDB connection"""
    url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
    token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
    org = os.getenv("INFLUXDB_ORG", "monitoring")
    bucket = os.getenv("INFLUXDB_BUCKET", "metrics")
    
    client = InfluxDBClient(url=url, token=token, org=org)
    return client, client.write_api(write_options=SYNCHRONOUS), client.query_api(), bucket