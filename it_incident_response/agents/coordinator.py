import uuid
import logging
import datetime
from typing import Dict, List, Any, Optional

from it_incident_response.agents.base import A2AAgent
from it_incident_response.protocols.a2a import (
    AgentCard, AgentCapability, A2AMessage, A2ATask,
    TaskState, PartType, MessagePart
)
from it_incident_response.protocols.mcp import MCPHost
from it_incident_response.models.incident import (
    create_incident, get_incident_by_id, update_incident_status,
    assign_incident, add_incident_note
)

logger = logging.getLogger("it-incident-response.agents.coordinator")

class IncidentCoordinatorAgent(A2AAgent):
    """Central coordinator for incident response"""

    def __init__(self, mcp_host: MCPHost):
        agent_card = AgentCard(
            agent_id="incident-coordinator",
            name="IT Incident Coordinator",
            description="Coordinates incident response workflow and delegates tasks to specialized agents",
            version="1.0.0",
            base_url="http://localhost:8000/incident-coordinator",
            capabilities=[
                AgentCapability(
                    name="create_incident",
                    description="Create a new incident",
                    parameters={
                        "title": {"type": "string", "description": "Incident title"},
                        "description": {"type": "string", "description": "Incident description"},
                        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                        "affected_systems": {"type": "array", "items": {"type": "string"}}
                    }
                ),
                AgentCapability(
                    name="get_incident_status",
                    description="Get the status of an incident",
                    parameters={
                        "incident_id": {"type": "string", "description": "Incident ID"}
                    }
                ),
                AgentCapability(
                    name="update_incident",
                    description="Update an incident",
                    parameters={
                        "incident_id": {"type": "string", "description": "Incident ID"},
                        "status": {"type": "string", "enum": ["investigating", "identified", "resolving", "resolved", "closed"]},
                        "notes": {"type": "string", "description": "Additional notes"}
                    }
                )
            ]
        )
        super().__init__(agent_card, mcp_host)
        self.diagnostic_agent_id = None
        self.resolution_agent_id = None

    def set_collaborating_agents(self, diagnostic_agent_id: str, resolution_agent_id: str):
        """Set the IDs of collaborating agents"""
        self.diagnostic_agent_id = diagnostic_agent_id
        self.resolution_agent_id = resolution_agent_id
        logger.info(f"Collaborating agents set: diagnostic={diagnostic_agent_id}, resolution={resolution_agent_id}")

    def _process_message(self, task: A2ATask, message: A2AMessage) -> None:
        """Process incoming messages to the coordinator"""
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
        if "create_incident" in request_data:
            # Create a new incident
            incident_data = request_data["create_incident"]

            incident_id = create_incident(
                title=incident_data.get("title", "Unknown incident"),
                description=incident_data.get("description", ""),
                severity=incident_data.get("severity", "medium"),
                affected_systems=incident_data.get("affected_systems", []),
                tags=incident_data.get("tags", [])
            )

            # Use MCP to log the incident in the ticketing system
            self.execute_mcp_tool("ticketing-system", {
                "action": "create_ticket",
                "data": get_incident_by_id(incident_id)
            })

            # Assign to diagnostic agent if available
            if self.diagnostic_agent_id:
                self._assign_to_diagnostic_agent(incident_id)

            # Add response parts
            response.add_text_part(f"Incident created with ID: {incident_id}")
            response.add_json_part({"incident": get_incident_by_id(incident_id)})

        elif "get_incident_status" in request_data:
            # Get incident status
            incident_id = request_data["get_incident_status"].get("incident_id")
            incident = get_incident_by_id(incident_id)

            if incident:
                response.add_text_part(f"Current status of incident {incident_id}: {incident.get('status')}")
                response.add_json_part({"incident": incident})
            else:
                response.add_text_part(f"Incident {incident_id} not found")

        elif "update_incident" in request_data:
            # Update incident
            incident_data = request_data["update_incident"]
            incident_id = incident_data.get("incident_id")

            incident = get_incident_by_id(incident_id)
            if not incident:
                response.add_text_part(f"Incident {incident_id} not found")
                task.add_message(response)
                task.update_state(TaskState.COMPLETED)
                return

            # Update status if provided
            if "status" in incident_data:
                status = incident_data["status"]
                notes = incident_data.get("notes")

                success = update_incident_status(incident_id, status, notes)
                if not success:
                    response.add_text_part(f"Failed to update incident status to {status}")
                    task.add_message(response)
                    task.update_state(TaskState.COMPLETED)
                    return

                # Update ticket in ticketing system
                self.execute_mcp_tool("ticketing-system", {
                    "action": "update_ticket",
                    "ticket_id": incident_id,
                    "data": {
                        "status": status,
                        "notes": notes
                    }
                })

                # If status changed to "identified", assign to resolution agent
                if status == "identified" and self.resolution_agent_id:
                    self._assign_to_resolution_agent(incident_id)

                # If status changed to "resolved", send notification
                if status == "resolved":
                    self.execute_mcp_tool("alert-system", {
                        "action": "create_alert",
                        "recipients": ["it-team@example.com", "stakeholders@example.com"],
                        "subject": f"Incident {incident_id} Resolved",
                        "message": f"The incident '{incident.get('title')}' has been resolved.\n\nNotes: {notes}",
                        "severity": "info"
                    })

            # Get updated incident
            updated_incident = get_incident_by_id(incident_id)
            response.add_text_part(f"Incident {incident_id} updated")
            response.add_json_part({"incident": updated_incident})

        else:
            response.add_text_part("Unknown request")

        # Add the response to the task
        task.add_message(response)
        task.update_state(TaskState.COMPLETED)

    def _assign_to_diagnostic_agent(self, incident_id: str) -> None:
        """Assign an incident to the diagnostic agent for analysis"""
        if not self.diagnostic_agent_id:
            logger.warning("Diagnostic agent not set")
            return

        logger.info(f"Assigning incident {incident_id} to diagnostic agent")

        # In a real implementation, this would use A2A to communicate with the diagnostic agent
        # For this prototype, we'll just log the assignment and update the incident
        incident = get_incident_by_id(incident_id)
        if incident:
            assign_incident(incident_id, f"diagnostic-agent:{self.diagnostic_agent_id}")
            add_incident_note(incident_id, f"Assigned to diagnostic agent for analysis")

            # Send notification via alert system
            self.execute_mcp_tool("alert-system", {
                "action": "create_alert",
                "recipients": ["it-team@example.com"],
                "subject": f"Incident {incident_id} Assigned for Diagnosis",
                "message": f"The incident '{incident.get('title')}' has been assigned to the diagnostic agent for analysis.",
                "severity": incident.get("severity", "medium")
            })

    def _assign_to_resolution_agent(self, incident_id: str) -> None:
        """Assign an incident to the resolution agent for remediation"""
        if not self.resolution_agent_id:
            logger.warning("Resolution agent not set")
            return

        logger.info(f"Assigning incident {incident_id} to resolution agent")

        # In a real implementation, this would use A2A to communicate with the resolution agent
        # For this prototype, we'll just log the assignment and update the incident
        incident = get_incident_by_id(incident_id)
        if incident:
            assign_incident(incident_id, f"resolution-agent:{self.resolution_agent_id}")
            add_incident_note(incident_id, f"Assigned to resolution agent for implementation")

            # Send notification via alert system
            self.execute_mcp_tool("alert-system", {
                "action": "create_alert",
                "recipients": ["it-team@example.com"],
                "subject": f"Incident {incident_id} Assigned for Resolution",
                "message": f"The incident '{incident.get('title')}' has been assigned to the resolution agent for implementation.",
                "severity": incident.get("severity", "medium")
            })
