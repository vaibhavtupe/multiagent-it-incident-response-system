import datetime
import logging
from typing import Dict, List, Any, Optional

from it_incident_response.protocols.mcp import MCPTool, MCPToolType
from it_incident_response.simulation.system_data import generate_system_metrics_for_incident

logger = logging.getLogger("it-incident-response.tools.system-monitor")

class SystemMonitorTool(MCPTool):
    """System Monitor tool implementation"""

    def __init__(self):
        super().__init__(
            tool_id="system-monitor",
            tool_type=MCPToolType.SYSTEM_MONITOR,
            name="System Monitor",
            description="Monitors system health metrics and performance",
            api_endpoint="http://localhost:8001/mcp/system-monitor",
            parameters={
                "incident_id": {"type": "string", "description": "ID of the incident to fetch system data for"},
                "servers": {"type": "array", "description": "List of servers to monitor", "default": []},
                "metrics": {"type": "array", "description": "List of metrics to include", "default": []}
            }
        )
        # Store system metrics for simulated monitoring
        self.incident_metrics: Dict[str, List[Dict[str, Any]]] = {}

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute system monitoring with provided parameters"""
        if not params:
            params = {}

        incident_id = params.get("incident_id")
        if not incident_id:
            return {"status": "error", "message": "Missing required parameter: incident_id"}

        # Get or generate metrics for this incident
        metrics = self.get_metrics_for_incident(incident_id)

        # Apply filters
        servers = params.get("servers", [])
        metric_names = params.get("metrics", [])

        filtered_metrics = self.filter_metrics(metrics, servers, metric_names)

        # Analyze the metrics
        analysis = self.analyze_metrics(filtered_metrics)

        return {
            "status": "success",
            "data": {
                "metrics_count": len(filtered_metrics),
                "metrics": filtered_metrics[:5],  # Limited sample for the response
                "anomalies": analysis["anomalies"],
                "thresholds_exceeded": analysis["thresholds_exceeded"],
                "performance_summary": analysis["performance_summary"],
                "timestamp": datetime.datetime.now().isoformat()
            }
        }

    def get_metrics_for_incident(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get metrics for an incident, generating them if needed"""
        if incident_id not in self.incident_metrics:
            # Simulate fetching metrics for this incident
            from it_incident_response.models.incident import get_incident_by_id
            incident = get_incident_by_id(incident_id)

            if incident:
                self.incident_metrics[incident_id] = generate_system_metrics_for_incident(incident)
            else:
                # Default metrics if incident not found
                self.incident_metrics[incident_id] = generate_system_metrics_for_incident(
                    {"affected_systems": ["db-server-01"], "tags": ["database"]}
                )

        return self.incident_metrics[incident_id]

    def filter_metrics(self, metrics: List[Dict[str, Any]],
                       servers: List[str], metric_names: List[str]) -> List[Dict[str, Any]]:
        """Filter metrics based on parameters"""
        if not servers and not metric_names:
            return metrics

        filtered = []
        for metric in metrics:
            # Server filter
            if servers and metric.get("server_id") not in servers:
                continue

            # Metric name filter
            if metric_names:
                # Create a filtered copy of the metrics
                filtered_metric = metric.copy()
                filtered_metric["metrics"] = {
                    k: v for k, v in metric.get("metrics", {}).items()
                    if k in metric_names
                }
                if filtered_metric["metrics"]:  # Only add if it has metrics after filtering
                    filtered.append(filtered_metric)
            else:
                filtered.append(metric)

        return filtered

    def analyze_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze metrics to identify anomalies and performance issues"""
        # Define thresholds for common metrics
        thresholds = {
            "cpu_usage_percent": 80,
            "memory_usage_percent": 85,
            "disk_usage_percent": 90,
            "error_rate_percent": 5,
            "response_time_ms": 500
        }

        anomalies = []
        thresholds_exceeded = []

        # Check each metric against thresholds
        for metric_obj in metrics:
            server_id = metric_obj.get("server_id", "unknown")
            server_type = metric_obj.get("server_type", "unknown")

            for metric_name, metric_value in metric_obj.get("metrics", {}).items():
                # Check if metric exceeds threshold
                if metric_name in thresholds and metric_value > thresholds[metric_name]:
                    thresholds_exceeded.append({
                        "server_id": server_id,
                        "metric": metric_name,
                        "value": metric_value,
                        "threshold": thresholds[metric_name]
                    })

                # Check for specific anomalies based on server type
                if server_type == "database" and metric_name == "connection_time_ms" and metric_value > 500:
                    anomalies.append({
                        "server_id": server_id,
                        "type": "database_connection_slow",
                        "details": f"Database connection time is {metric_value}ms, exceeding normal threshold of 500ms"
                    })
                elif metric_name == "network_latency_ms" and metric_value > 50:
                    anomalies.append({
                        "server_id": server_id,
                        "type": "network_latency_high",
                        "details": f"Network latency is {metric_value}ms, exceeding normal threshold of 50ms"
                    })

        # Generate performance summary
        if thresholds_exceeded:
            performance_summary = "Performance issues detected"
        else:
            performance_summary = "System performance within normal parameters"

        return {
            "anomalies": anomalies,
            "thresholds_exceeded": thresholds_exceeded,
            "performance_summary": performance_summary
        }