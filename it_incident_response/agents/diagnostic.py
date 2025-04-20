import uuid
import logging
import datetime
import time
from typing import Dict, List, Any, Optional

from it_incident_response.agents.base import A2AAgent
from it_incident_response.protocols.a2a import (
    AgentCard, AgentCapability, A2AMessage, A2ATask,
    TaskState, PartType, MessagePart
)
from it_incident_response.protocols.mcp import MCPHost
from it_incident_response.models.incident import get_incident_by_id, update_incident_status, add_incident_note
from it_incident_response.models.diagnostic import (
    create_diagnostic_report, get_report_by_id, update_report_status,
    set_report_root_cause, add_report_evidence, add_report_action, add_report_reference
)

logger = logging.getLogger("it-incident-response.agents.diagnostic")

class DiagnosticAgent(A2AAgent):
    """Agent responsible for analyzing and diagnosing incidents"""

    def __init__(self, mcp_host: MCPHost):
        agent_card = AgentCard(
            agent_id="diagnostic-agent",
            name="IT Diagnostic Agent",
            description="Analyzes system data and logs to diagnose the root cause of incidents",
            version="1.0.0",
            base_url="http://localhost:8000/diagnostic-agent",
            capabilities=[
                AgentCapability(
                    name="analyze_incident",
                    description="Analyze an incident to determine root cause",
                    parameters={
                        "incident_id": {"type": "string", "description": "Incident ID"}
                    }
                ),
                AgentCapability(
                    name="get_diagnostic_report",
                    description="Get the diagnostic report for an incident",
                    parameters={
                        "incident_id": {"type": "string", "description": "Incident ID"}
                    }
                )
            ]
        )
        super().__init__(agent_card, mcp_host)

    def _process_message(self, task: A2ATask, message: A2AMessage) -> None:
        """Process incoming messages to the diagnostic agent"""
        task.update_state(TaskState.WORKING)

        # Extract the request from the message parts
        request_data = {}
        for part in message.parts:
            if part.content_type == PartType.JSON:
                request_data = part.content
                break

        # Create response message
        response = A2AMessage(
            message_id=str(uuid.uuid4()),
            role="agent"
        )

        # Process based on the requested capability
        if "analyze_incident" in request_data:
            # Analyze an incident
            incident_id = request_data["analyze_incident"].get("incident_id")
            logger.info(f"Analyzing incident: {incident_id}")

            incident = get_incident_by_id(incident_id)
            if not incident:
                response.add_text_part(f"Incident {incident_id} not found")
                task.add_message(response)
                task.update_state(TaskState.COMPLETED)
                return

            # Create a diagnostic report
            report_id = create_diagnostic_report(incident_id)
            update_report_status(report_id, "in_progress")

            # Use MCP tools to gather data for diagnosis
            log_data = self.execute_mcp_tool("log-analyzer", {
                "incident_id": incident_id,
                "time_range": "1h",
                "log_level": "WARN"
            })

            system_data = self.execute_mcp_tool("system-monitor", {
                "incident_id": incident_id,
                "servers": incident.get("affected_systems", [])
            })

            # Simulate diagnostic analysis
            time.sleep(1)  # Simulate processing time

            # Determine root cause based on log patterns and system metrics
            root_cause = None
            confidence = 0.0
            evidence = []
            recommended_actions = []

            # Extract patterns from log data
            if log_data.get("status") == "success":
                log_patterns = log_data.get("data", {}).get("log_patterns", [])

                if log_patterns:
                    # Look for specific patterns in the logs
                    if any("connection timeout" in pattern.lower() for pattern in log_patterns):
                        root_cause = "Database connection timeout due to network latency spike"
                        confidence = 0.92
                        evidence.append("Multiple connection timeout errors in application logs")
                    elif any("memory" in pattern.lower() for pattern in log_patterns):
                        root_cause = "Memory leak in authentication service"
                        confidence = 0.87
                        evidence.append("Increasing memory usage pattern observed in logs")
                    elif any("circuit breaker" in pattern.lower() for pattern in log_patterns):
                        root_cause = "API Gateway circuit breaker triggered due to backend service failures"
                        confidence = 0.90
                        evidence.append("Circuit breaker activation events in API Gateway logs")
                    elif any("disk" in pattern.lower() for pattern in log_patterns):
                        root_cause = "Critical disk space shortage on storage nodes"
                        confidence = 0.95
                        evidence.append("Disk space warnings in system logs")

            # Extract evidence from system data
            if system_data.get("status") == "success":
                anomalies = system_data.get("data", {}).get("anomalies", [])

                if anomalies:
                    for anomaly in anomalies:
                        evidence.append(anomaly.get("details", "System anomaly detected"))

                    # If no root cause identified from logs, try from system anomalies
                    if not root_cause:
                        if any("network_latency_high" in anomaly.get("type", "") for anomaly in anomalies):
                            root_cause = "Network latency spike between application and database servers"
                            confidence = 0.85
                        elif any("database_connection_slow" in anomaly.get("type", "") for anomaly in anomalies):
                            root_cause = "Slow database connections due to connection pool exhaustion"
                            confidence = 0.88

            # If still no root cause, use a generic one
            if not root_cause:
                root_cause = "Intermittent system performance degradation"
                confidence = 0.70
                evidence.append("Multiple error patterns with no clear primary cause")

            # Add time correlation evidence
            evidence.append("Errors coincide with period of increased system load")

            # Determine recommended actions based on root cause
            if "database connection timeout" in root_cause.lower():
                recommended_actions = [
                    "Increase database connection timeout parameters",
                    "Implement connection pooling with proper sizing",
                    "Monitor network latency between app and database servers",
                    "Consider adding retry logic with exponential backoff",
                    "Review database performance and tuning"
                ]
            elif "memory leak" in root_cause.lower():
                recommended_actions = [
                    "Review recent code changes in authentication service",
                    "Check for improper resource cleanup in session management",
                    "Implement memory usage monitoring and alerting",
                    "Restart service during low-traffic period",
                    "Apply memory leak patch from development team"
                ]
            elif "api gateway" in root_cause.lower():
                recommended_actions = [
                    "Check health of backend services",
                    "Adjust circuit breaker thresholds if needed",
                    "Implement fallback mechanisms for critical services",
                    "Scale up backend services to handle current load",
                    "Review API Gateway configuration"
                ]
            elif "disk space" in root_cause.lower():
                recommended_actions = [
                    "Clean temporary files and logs",
                    "Expand storage capacity for affected nodes",
                    "Implement data retention policies",
                    "Move non-critical data to secondary storage",
                    "Set up proactive disk space monitoring"
                ]
            else:
                recommended_actions = [
                    "Monitor system for additional error patterns",
                    "Review recent system changes and deployments",
                    "Temporarily increase resources for affected services",
                    "Implement additional logging for better diagnosis",
                    "Schedule comprehensive system review"
                ]

            # Update the diagnostic report
            set_report_root_cause(report_id, root_cause, confidence)
            for item in evidence:
                add_report_evidence(report_id, item)

            for action in recommended_actions:
                add_report_action(report_id, action)

            # Use knowledge base to enhance recommendations
            kb_data = self.execute_mcp_tool("knowledge-base", {
                "query": root_cause,
                "max_results": 3
            })

            if kb_data.get("status") == "success":
                kb_articles = kb_data.get("data", {}).get("articles", [])
                for article in kb_articles:
                    add_report_reference(report_id, article)

            # Update report status to completed
            update_report_status(report_id, "completed")

            # Update incident with diagnostic findings
            add_incident_note(incident_id, f"Diagnostic analysis completed. Root cause: {root_cause}")

            # Add response parts
            response.add_text_part(f"Analysis complete for incident {incident_id}")
            response.add_json_part({"diagnostic_report": get_report_by_id(report_id)})

        elif "get_diagnostic_report" in request_data:
            # Get diagnostic report for an incident
            incident_id = request_data["get_diagnostic_report"].get("incident_id")

            from it_incident_response.models.diagnostic import get_report_by_incident_id
            report = get_report_by_incident_id(incident_id)

            if report:
                response.add_text_part(f"Diagnostic report for incident {incident_id}")
                response.add_json_part({"diagnostic_report": report})
            else:
                response.add_text_part(f"No diagnostic report found for incident {incident_id}")

        else:
            response.add_text_part("Unknown request")

        # Add the response to the task
        task.add_message(response)
        task.update_state(TaskState.COMPLETED)
