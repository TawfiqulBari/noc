from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class AlertManager:
    def __init__(self):
        self.influxdb = InfluxDBClient(
            url=os.getenv("INFLUXDB_URL", "http://influxdb:8086"),
            token=os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token"),
            org=os.getenv("INFLUXDB_ORG", "monitoring")
        )
        self.query_api = self.influxdb.query_api()
        
        # Alert thresholds
        self.thresholds = {
            "cpu": 90,
            "memory": 85,
            "container_down": True
        }
        
        # Notification config
        self.smtp_config = {
            "host": os.getenv("SMTP_HOST", "smtp.example.com"),
            "port": int(os.getenv("SMTP_PORT", 587)),
            "username": os.getenv("SMTP_USER", "user@example.com"),
            "password": os.getenv("SMTP_PASS", "password"),
            "from_email": os.getenv("ALERT_FROM_EMAIL", "alerts@monitoring.com"),
            "to_email": os.getenv("ALERT_TO_EMAIL", "admin@example.com")
        }

    def check_thresholds(self):
        """Check all configured thresholds and generate alerts"""
        alerts = []
        
        # Check CPU threshold
        cpu_query = '''
        from(bucket: "metrics")
          |> range(start: -5m)
          |> filter(fn: (r) => r._measurement == "system_metrics")
          |> filter(fn: (r) => r._field == "cpu_usage")
          |> mean()
        '''
        cpu_result = self.query_api.query(cpu_query)
        if cpu_result and cpu_result[0].records[0].get_value() > self.thresholds["cpu"]:
            alerts.append({
                "severity": "critical",
                "message": f"High CPU usage detected: {cpu_result[0].records[0].get_value()}%",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active"
            })
        
        # Check Memory threshold
        mem_query = '''
        from(bucket: "metrics")
          |> range(start: -5m)
          |> filter(fn: (r) => r._measurement == "system_metrics")
          |> filter(fn: (r) => r._field == "memory_usage")
          |> mean()
        '''
        mem_result = self.query_api.query(mem_query)
        if mem_result and mem_result[0].records[0].get_value() > self.thresholds["memory"]:
            alerts.append({
                "severity": "warning",
                "message": f"High Memory usage detected: {mem_result[0].records[0].get_value()}%",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active"
            })
        
        return alerts

    def send_email_alert(self, alert):
        """Send alert via email"""
        msg = MIMEText(f"""
        Alert Details:
        Severity: {alert['severity']}
        Message: {alert['message']}
        Time: {alert['timestamp']}
        """)
        
        msg['Subject'] = f"[{alert['severity'].upper()}] Monitoring Alert"
        msg['From'] = self.smtp_config["from_email"]
        msg['To'] = self.smtp_config["to_email"]
        
        try:
            with smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"]) as server:
                server.starttls()
                server.login(self.smtp_config["username"], self.smtp_config["password"])
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email alert: {e}")

    def process_alerts(self):
        """Main alert processing loop"""
        alerts = self.check_thresholds()
        for alert in alerts:
            self.send_email_alert(alert)
            # Store alert in InfluxDB
            point = Point("alerts")\
                .tag("severity", alert["severity"])\
                .field("message", alert["message"])\
                .field("status", alert["status"])
            write_api = self.influxdb.write_api(write_options=SYNCHRONOUS)
            write_api.write(
                bucket=os.getenv("INFLUXDB_BUCKET", "metrics"),
                record=point
            )

if __name__ == "__main__":
    alert_manager = AlertManager()
    alert_manager.process_alerts()