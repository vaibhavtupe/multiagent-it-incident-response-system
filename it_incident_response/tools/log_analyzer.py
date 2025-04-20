import datetime
import logging
from typing import Dict, List, Any, Optional

from it_incident_response.protocols.mcp import MCPTool, MCPToolType
from it_incident_response.simulation.log_data import get_logs_for_incident

logger = logging.getLogger("it-incident-response.tools.log-analyzer")

class LogAnalyzerTool(MCPTool):
    """Log Analyzer tool implementation"""

    def __init__(self):
        super().__init__(
            tool_id="log-analyzer",
            tool_type=MCPToolType.LOG_ANALYZER,
            name="Log Analyzer",
            description="Analyzes system logs to identify patterns and anomalies",
            api_endpoint="http://localhost:8001/mcp/log-analyzer",
            parameters={
                "incident_id": {"type": "string", "description": "ID of the incident to analyze logs for"},
                "time_range": {"type": "string", "description": "Time range for log analysis (e.g., '1h', '24h')"},
                "log_level": {"type": "string", "description": "Minimum log level to include", "default": "WARN"},
                "services": {"type": "array", "description": "List of services to include", "default": []}
            }
        )
        # Store incident logs for simulated analysis
        self.incident_logs: Dict[str, List[Dict[str, Any]]] = {}

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute log analysis with provided parameters"""
        if not params:
            params = {}

        incident_id = params.get("incident_id")
        if not incident_id:
            return {"status": "error", "message": "Missing required parameter: incident_id"}

        # Get or generate logs for this incident
        logs = self.get_logs_for_incident(incident_id)

        # Apply filters
        time_range = params.get("time_range", "24h")
        log_level = params.get("log_level", "WARN")
        services = params.get("services", [])

        filtered_logs = self.filter_logs(logs, time_range, log_level, services)

        # Analyze patterns in the logs
        patterns = self.analyze_log_patterns(filtered_logs)

        return {
            "status": "success",
            "data": {
                "log_count": len(filtered_logs),
                "log_entries": filtered_logs[:10],  # Limited sample for the response
                "log_patterns": patterns["patterns"],
                "anomalies_detected": patterns["anomalies_detected"],
                "severity": patterns["severity"],
                "timestamp": datetime.datetime.now().isoformat()
            }
        }

    def get_logs_for_incident(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get logs for an incident, generating them if needed"""
        if incident_id not in self.incident_logs:
            # Simulate fetching logs for this incident from an incident management system
            # For simulation, we'll just use placeholder incident data
            from it_incident_response.models.incident import get_incident_by_id
            incident = get_incident_by_id(incident_id)

            if incident:
                self.incident_logs[incident_id] = get_logs_for_incident(incident)
            else:
                # Default logs if incident not found
                self.incident_logs[incident_id] = get_logs_for_incident({"tags": ["database"]})

        return self.incident_logs[incident_id]

    def filter_logs(self, logs: List[Dict[str, Any]], time_range: str,
                    min_log_level: str, services: List[str]) -> List[Dict[str, Any]]:
        """Filter logs based on parameters"""
        # Convert time range to datetime
        now = datetime.datetime.now()
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = now - datetime.timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = now - datetime.timedelta(days=days)
        else:
            # Default to 24 hours
            start_time = now - datetime.timedelta(hours=24)

        start_time_str = start_time.isoformat()

        # Log level hierarchy for filtering
        log_levels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
        min_level_idx = log_levels.index(min_log_level) if min_log_level in log_levels else 0

        filtered = []
        for log in logs:
            # Time filter
            if log.get("timestamp", "") >= start_time_str:
                # Level filter
                log_level = log.get("level", "INFO")
                level_idx = log_levels.index(log_level) if log_level in log_levels else 0

                if level_idx >= min_level_idx:
                    # Service filter
                    if not services or log.get("service", "") in services:
                        filtered.append(log)

        return filtered

    def analyze_log_patterns(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze logs to find patterns and anomalies"""
        # Count occurrences of each error message
        message_counts = {}
        for log in logs:
            message = log.get("message", "")
            message_counts[message] = message_counts.get(message, 0) + 1

        # Sort by frequency
        sorted_messages = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)

        # Extract patterns (most common error messages)
        patterns = [msg for msg, count in sorted_messages[:5]]

        # Determine if anomalies are present and severity
        error_count = sum(1 for log in logs if log.get("level") in ["ERROR", "CRITICAL"])
        anomalies_detected = error_count > 0

        if error_count > 10:
            severity = "critical"
        elif error_count > 5:
            severity = "high"
        elif error_count > 0:
            severity = "medium"
        else:
            severity = "low"

        return {
            "patterns": patterns,
            "anomalies_detected": anomalies_detected,
            "severity": severity
        }
