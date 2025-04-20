import datetime
import logging
import uuid
from typing import Dict, List, Any, Optional

from it_incident_response.protocols.mcp import MCPTool, MCPToolType

logger = logging.getLogger("it-incident-response.tools.alert")

class AlertSystemTool(MCPTool):
    """Alert System tool implementation"""

    def __init__(self):
        super().__init__(
            tool_id="alert-system",
            tool_type=MCPToolType.ALERT_SYSTEM,
            name="Alert System",
            description="Sends alerts and notifications to IT teams",
            api_endpoint="http://localhost:8001/mcp/alert-system",
            parameters={
                "action": {"type": "string", "description": "Action to perform (create_alert, acknowledge_alert)"},
                "alert_id": {"type": "string", "description": "ID of the alert (for acknowledgements)"},
                "recipients": {"type": "array", "description": "List of recipients for the alert"},
                "subject": {"type": "string", "description": "Alert subject"},
                "message": {"type": "string", "description": "Alert message content"},
                "severity": {"type": "string", "description": "Alert severity", "default": "medium"}
            }
        )
        # Store alerts for simulation
        self.alerts: Dict[str, Dict[str, Any]] = {}

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute alert system operations with provided parameters"""
        if not params:
            params = {}

        action = params.get("action")
        if not action:
            return {"status": "error", "message": "Missing required parameter: action"}

        if action == "create_alert":
            return self._create_alert(params)
        elif action == "acknowledge_alert":
            alert_id = params.get("alert_id")
            if not alert_id:
                return {"status": "error", "message": "Missing required parameter: alert_id"}
            return self._acknowledge_alert(alert_id, params.get("acknowledger"))
        else:
            return {"status": "error", "message": f"Unsupported action: {action}"}

    def _create_alert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert"""
        required_params = ["recipients", "subject", "message"]
        for param in required_params:
            if param not in params:
                return {"status": "error", "message": f"Missing required parameter: {param}"}

        # Generate alert ID
        alert_id = str(uuid.uuid4())

        # Create alert
        alert = {
            "alert_id": alert_id,
            "recipients": params.get("recipients"),
            "subject": params.get("subject"),
            "message": params.get("message"),
            "severity": params.get("severity", "medium"),
            "created_at": datetime.datetime.now().isoformat(),
            "status": "sent",
            "acknowledged": False
        }

        self.alerts[alert_id] = alert
        logger.info(f"Alert created: {alert_id} - {alert['subject']}")

        return {
            "status": "success",
            "data": {
                "alert_id": alert_id,
                "alert": alert
            }
        }

    def _acknowledge_alert(self, alert_id: str, acknowledger: str = None) -> Dict[str, Any]:
        """Acknowledge an existing alert"""
        if alert_id not in self.alerts:
            return {"status": "error", "message": f"Alert not found: {alert_id}"}

        # Update alert status
        alert = self.alerts[alert_id]
        alert["acknowledged"] = True
        alert["acknowledged_at"] = datetime.datetime.now().isoformat()

        if acknowledger:
            alert["acknowledged_by"] = acknowledger

        logger.info(f"Alert acknowledged: {alert_id}")

        return {
            "status": "success",
            "data": {
                "alert_id": alert_id,
                "alert": alert
            }
        }