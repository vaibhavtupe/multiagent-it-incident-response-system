import datetime
import logging
import uuid
from typing import Dict, List, Any, Optional

from it_incident_response.protocols.mcp import MCPTool, MCPToolType

logger = logging.getLogger("it-incident-response.tools.ticketing")

class TicketingSystemTool(MCPTool):
    """Ticketing System tool implementation"""

    def __init__(self):
        super().__init__(
            tool_id="ticketing-system",
            tool_type=MCPToolType.TICKETING_SYSTEM,
            name="Ticketing System",
            description="Creates and manages incident tickets",
            api_endpoint="http://localhost:8001/mcp/ticketing-system",
            parameters={
                "action": {"type": "string", "description": "Action to perform (create_ticket, update_ticket, get_ticket)"},
                "ticket_id": {"type": "string", "description": "ID of the ticket (for updates or retrieval)"},
                "data": {"type": "object", "description": "Ticket data for creation or updates"}
            }
        )
        # Store tickets for simulation
        self.tickets: Dict[str, Dict[str, Any]] = {}

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute ticketing system operations with provided parameters"""
        if not params:
            params = {}

        action = params.get("action")
        if not action:
            return {"status": "error", "message": "Missing required parameter: action"}

        if action == "create_ticket":
            return self._create_ticket(params.get("data", {}))
        elif action == "update_ticket":
            ticket_id = params.get("ticket_id")
            if not ticket_id:
                return {"status": "error", "message": "Missing required parameter: ticket_id"}
            return self._update_ticket(ticket_id, params.get("data", {}))
        elif action == "get_ticket":
            ticket_id = params.get("ticket_id")
            if not ticket_id:
                return {"status": "error", "message": "Missing required parameter: ticket_id"}
            return self._get_ticket(ticket_id)
        else:
            return {"status": "error", "message": f"Unsupported action: {action}"}

    def _create_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ticket"""
        if not data:
            return {"status": "error", "message": "Empty ticket data"}

        # Generate ticket ID if not provided
        ticket_id = data.get("incident_id") or str(uuid.uuid4())

        # Create ticket with metadata
        ticket = data.copy()
        ticket.update({
            "ticket_id": ticket_id,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "status": data.get("status", "open")
        })

        self.tickets[ticket_id] = ticket
        logger.info(f"Ticket created: {ticket_id}")

        return {
            "status": "success",
            "data": {
                "ticket_id": ticket_id,
                "ticket": ticket
            }
        }

    def _update_ticket(self, ticket_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing ticket"""
        if ticket_id not in self.tickets:
            return {"status": "error", "message": f"Ticket not found: {ticket_id}"}

        # Update ticket
        ticket = self.tickets[ticket_id]
        ticket.update(data)
        ticket["updated_at"] = datetime.datetime.now().isoformat()

        logger.info(f"Ticket updated: {ticket_id}")

        return {
            "status": "success",
            "data": {
                "ticket_id": ticket_id,
                "ticket": ticket
            }
        }

    def _get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Get an existing ticket"""
        if ticket_id not in self.tickets:
            return {"status": "error", "message": f"Ticket not found: {ticket_id}"}

        return {
            "status": "success",
            "data": {
                "ticket_id": ticket_id,
                "ticket": self.tickets[ticket_id]
            }
        }