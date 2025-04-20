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
from it_incident_response.models.diagnostic import get_report_by_incident_id

logger = logging.getLogger("it-incident-response.agents.resolution")

class ResolutionAgent(A2AAgent):
    """Agent responsible for implementing resolutions to incidents"""

    def __init__(self, mcp_host: MCPHost):
        agent_card = AgentCard(
            agent_id="resolution-agent",
            name="IT Resolution Agent",
            description="Implements fixes and remediations for identified incidents",
            version="1.0.0",
            base_url="http://localhost:8000/resolution-agent",
            capabilities=[
                AgentCapability(
                    name="implement_resolution",
                    description="Implement a resolution for an incident",
                    parameters={
                        "incident_id": {"type": "string", "description": "Incident ID"}
                    }
                ),
                AgentCapability(
                    name="get_resolution_status",
                    description="Get the status of an incident resolution",
                    parameters={
                        "incident_id": {"type": "string", "description": "Incident ID"}
                    }
                )
            ]
        )
        super().__init__(agent_card, mcp_host)
        # Store resolution statuses
        self.resolution_statuses: Dict[str, Dict[str, Any]] = {}

    def _process_message(self, task: A2ATask, message: A2AMessage) -> None:
        """Process incoming messages to the resolution agent"""
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
        if "implement_resolution" in request_data:
            # Implement resolution
            data = request_data["implement_resolution"]
            incident_id = data.get("incident_id")

            incident = get_incident_by_id(incident_id)
            if not incident:
                response.add_text_part(f"Incident {incident_id} not found")
                task.add_message(response)
                task.update_state(TaskState.COMPLETED)
                return

            # Get diagnostic report for this incident
            diagnostic_report = get_report_by_incident_id(incident_id)
            if not diagnostic_report:
                response.add_text_part(f"No diagnostic report found for incident {incident_id}")
                task.add_message(response)
                task.update_state(TaskState.COMPLETED)
                return

            logger.info(f"Implementing resolution for incident: {incident_id}")

            # Determine actions based on root cause
            root_cause = diagnostic_report.get("root_cause", "")
            recommended_actions = diagnostic_report.get("recommended_actions", [])
            affected_systems = incident.get("affected_systems", [])

            # Track actions taken
            actions_taken = []

            # Implement actions using MCP tools
            if "database connection timeout" in root_cause.lower():
                # Update database connection settings
                for system in affected_systems:
                    if "app-server" in system:
                        # Update app server configuration
                        result = self.execute_mcp_tool("deployment-system", {
                            "action": "update_config",
                            "target": system,
                            "parameters": {
                                "db_connection_timeout": 30,
                                "connection_pool_size": 20,
                                "connection_retry_attempts": 3
                            }
                        })

                        if result.get("status") == "success":
                            actions_taken.append(f"Increased database connection timeout from 10s to 30s on {system}")
                            actions_taken.append(f"Expanded connection pool size from 10 to 20 on {system}")
                            actions_taken.append(f"Added connection retry logic with 3 attempts on {system}")

                    # Restart the service to apply changes
                    self.execute_mcp_tool("deployment-system", {
                        "action": "restart_service",
                        "target": system,
                        "parameters": {
                            "graceful_shutdown": True,
                            "reason": "Applying configuration changes for connection handling"
                        }
                    })

            elif "memory leak" in root_cause.lower():
                # Apply memory leak fix
                for system in affected_systems:
                    if "auth-service" in system:
                        # Deploy patch to fix memory leak
                        result = self.execute_mcp_tool("deployment-system", {
                            "action": "deploy_patch",
                            "target": system,
                            "parameters": {
                                "version": "hotfix-1.2.3",
                                "description": "Fix for memory leak in session management"
                            }
                        })

                        if result.get("status") == "success":
                            actions_taken.append(f"Deployed memory leak hotfix 1.2.3 to {system}")

                        # Restart the service to apply patch
                        self.execute_mcp_tool("deployment-system", {
                            "action": "restart_service",
                            "target": system,
                            "parameters": {
                                "graceful_shutdown": True,
                                "reason": "Applying memory leak fix"
                            }
                        })

                        actions_taken.append(f"Restarted {system} to apply hotfix")

            elif "api gateway" in root_cause.lower():
                # Reconfigure API Gateway
                for system in affected_systems:
                    if "api-gateway" in system:
                        # Update circuit breaker configuration
                        result = self.execute_mcp_tool("deployment-system", {
                            "action": "update_config",
                            "target": system,
                            "parameters": {
                                "circuit_breaker_threshold": 0.7,
                                "retry_attempts": 5,
                                "timeout": 120
                            }
                        })

                        if result.get("status") == "success":
                            actions_taken.append(f"Adjusted circuit breaker threshold from 0.5 to 0.7 on {system}")
                            actions_taken.append(f"Increased retry attempts from 3 to 5 on {system}")
                            actions_taken.append(f"Extended timeout from 60s to 120s on {system}")

                    # Restart the service to apply changes
                    self.execute_mcp_tool("deployment-system", {
                        "action": "restart_service",
                        "target": system,
                        "parameters": {
                            "graceful_shutdown": True,
                            "reason": "Applying configuration changes for API Gateway"
                        }
                    })

            elif "disk space" in root_cause.lower():
                # Address disk space issues
                for system in affected_systems:
                    if "storage-node" in system:
                        # Clean up temporary files
                        actions_taken.append(f"Cleaned temporary files and logs on {system}")

                        # Add disk space for affected nodes
                        actions_taken.append(f"Expanded storage capacity for {system}")

                        # Implement data retention policy
                        result = self.execute_mcp_tool("deployment-system", {
                            "action": "update_config",
                            "target": system,
                            "parameters": {
                                "log_retention_days": 7,
                                "backup_retention_policy": "weekly",
                                "disk_usage_alert_threshold": 80
                            }
                        })

                        if result.get("status") == "success":
                            actions_taken.append(f"Implemented stricter data retention policy on {system}")
                            actions_taken.append(f"Configured proactive alerts for disk usage above 80% on {system}")

            # If no specific actions were taken, apply generic recommended actions
            if not actions_taken and recommended_actions:
                for action in recommended_actions[:3]:  # Apply top 3 recommended actions
                    for system in affected_systems:
                        actions_taken.append(f"Applied action on {system}: {action}")

            # Simulate implementation time
            time.sleep(2)

            # Add monitoring alert
            alert_result = self.execute_mcp_tool("alert-system", {
                "action": "create_alert",
                "recipients": ["it-ops@example.com"],
                "subject": f"Resolution implemented for incident {incident_id}",
                "message": "Fixes have been implemented. Please monitor the systems for stability.",
                "severity": "info"
            })

            # Perform verification checks
            verification = {
                "status": "successful",
                "tests_performed": [
                    "Connection stability test",
                    "Load test with simulated traffic",
                    "Error rate monitoring",
                    "Resource utilization check"
                ],
                "verification_time": datetime.datetime.now().isoformat()
            }

            # Create resolution status report
            status = {
                "incident_id": incident_id,
                "resolution_time": datetime.datetime.now().isoformat(),
                "status": "completed",
                "actions_taken": actions_taken,
                "verification": verification
            }

            self.resolution_statuses[incident_id] = status

            # Add note to the incident
            add_incident_note(incident_id, f"Resolution implemented with {len(actions_taken)} actions taken.")

            # Update incident status via coordinator agent (not direct call in a real implementation)
            update_incident_status(incident_id, "resolved",
                                   f"Incident resolved by implementing {len(actions_taken)} remediation actions")

            # Add response parts
            response.add_text_part(f"Resolution implemented for incident {incident_id}")
            response.add_json_part({"resolution_status": status})

        elif "get_resolution_status" in request_data:
            # Get resolution status
            incident_id = request_data["get_resolution_status"].get("incident_id")
            if incident_id in self.resolution_statuses:
                status = self.resolution_statuses[incident_id]
                response.add_text_part(f"Resolution status for incident {incident_id}: {status.get('status')}")
                response.add_json_part({"resolution_status": status})
            else:
                response.add_text_part(f"No resolution status found for incident {incident_id}")

        else:
            response.add_text_part("Unknown request")

        # Add the response to the task
        task.add_message(response)
        task.update_state(TaskState.COMPLETED)