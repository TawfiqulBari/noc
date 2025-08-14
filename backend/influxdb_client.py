from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import os

class InfluxDBManager:
    def __init__(self):
        self.url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
        self.token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
        self.org = os.getenv("INFLUXDB_ORG", "monitoring")
        self.bucket = os.getenv("INFLUXDB_BUCKET", "metrics")
        
        self.client = InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write_metric(self, measurement, fields, tags=None):
        from influxdb_client import Point
        point = Point(measurement)
        
        if tags:
            for key, value in tags.items():
                point.tag(key, value)
                
        for key, value in fields.items():
            point.field(key, value)
            
        self.write_api.write(bucket=self.bucket, record=point)

    def query_metrics(self, query):
        try:
            result = self.query_api.query(query)
            return result
        except Exception as e:
            print(f"Error querying InfluxDB: {e}")
            return None

    def close(self):
        self.client.close()

# Singleton instance
influxdb_client = InfluxDBManager()