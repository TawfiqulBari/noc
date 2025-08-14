import psutil
import docker
import time
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# Initialize Docker client
docker_client = docker.from_env()

# Initialize InfluxDB client
influxdb = InfluxDBClient(
    url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
    token=os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token"),
    org=os.getenv("INFLUXDB_ORG", "monitoring")
)
write_api = influxdb.write_api(write_options=SYNCHRONOUS)

def collect_system_metrics():
    """Collect system-level metrics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        "cpu_usage": cpu_percent,
        "memory_usage": memory.percent,
        "memory_total": memory.total,
        "memory_used": memory.used
    }

def collect_docker_metrics():
    """Collect Docker container metrics"""
    containers = docker_client.containers.list()
    container_count = len(containers)
    
    container_metrics = []
    for container in containers:
        stats = container.stats(stream=False)
        container_metrics.append({
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "cpu_usage": stats['cpu_stats']['cpu_usage']['total_usage'],
            "memory_usage": stats['memory_stats']['usage'],
            "memory_limit": stats['memory_stats']['limit']
        })
    
    return {
        "container_count": container_count,
        "containers": container_metrics
    }

def send_metrics_to_influxdb():
    """Collect and send metrics to InfluxDB"""
    system_metrics = collect_system_metrics()
    docker_metrics = collect_docker_metrics()
    
    # System metrics point
    system_point = Point("system_metrics")\
        .field("cpu_usage", system_metrics["cpu_usage"])\
        .field("memory_usage", system_metrics["memory_usage"])\
        .field("memory_total", system_metrics["memory_total"])\
        .field("memory_used", system_metrics["memory_used"])\
        .field("container_count", docker_metrics["container_count"])
    
    write_api.write(
        bucket=os.getenv("INFLUXDB_BUCKET", "metrics"),
        record=system_point
    )
    
    # Container metrics points
    for container in docker_metrics["containers"]:
        container_point = Point("container_metrics")\
            .tag("container_id", container["id"])\
            .tag("container_name", container["name"])\
            .field("cpu_usage", container["cpu_usage"])\
            .field("memory_usage", container["memory_usage"])\
            .field("memory_limit", container["memory_limit"])\
            .field("status", 1 if container["status"] == "running" else 0)
        
        write_api.write(
            bucket=os.getenv("INFLUXDB_BUCKET", "metrics"),
            record=container_point
        )

if __name__ == "__main__":
    while True:
        try:
            send_metrics_to_influxdb()
            time.sleep(10)  # Collect every 10 seconds
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            time.sleep(30)  # Wait longer if error occurs