import uuid
import logging
from typing import Dict, List, Optional, Any, Union

from it_incident_response.protocols.a2a import (
    AgentCard, A2AMessage, A2ATask, TaskState
)
from it_incident_response.protocols.mcp import MCPHost

logger = logging.getLogger("it-incident-response.agents")

class A2AAgent:
    """Base class for an A2A-compatible agent with MCP integration"""

    def __init__(self, agent_card: AgentCard, mcp_host: Optional[MCPHost] = None):
        self.agent_card = agent_card
        self.mcp_host = mcp_host
        self.mcp_session_id = None
        self.tasks: Dict[str, A2ATask] = {}
        logger.info(f"Agent initialized: {agent_card.name} ({agent_card.agent_id})")

        # Initialize MCP session if host is provided
        if mcp_host:
            self.mcp_session_id = mcp_host.create_session(agent_card.agent_id)
            logger.info(f"MCP session created: {self.mcp_session_id}")

    def get_agent_card(self) -> Dict[str, Any]:
        """Return the agent card in JSON format"""
        return self.agent_card.to_dict()

    def create_task(self, initial_message: A2AMessage) -> str:
        """Create a new task with an initial message"""
        task_id = str(uuid.uuid4())
        task = A2ATask(
            task_id=task_id,
            state=TaskState.SUBMITTED,
            messages=[initial_message]
        )
        self.tasks[task_id] = task
        logger.info(f"Task created: {task_id}")
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        if task_id not in self.tasks:
            return None
        return self.tasks[task_id].to_dict()

    def send_message(self, task_id: str, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Send a message to an existing task"""
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return None

        task = self.tasks[task_id]
        task.add_message(message)
        logger.info(f"Message added to task {task_id}: {message.message_id}")

        # Process the message and update task state accordingly
        self._process_message(task, message)

        return task.to_dict()

    def _process_message(self, task: A2ATask, message: A2AMessage) -> None:
        """
        Process an incoming message

        This method should be implemented by agent subclasses to define
        their specific behavior when receiving messages.
        """
        # Default implementation just updates the state to WORKING
        task.update_state(TaskState.WORKING)
        logger.warning(f"Default message processing in base class for {self.agent_card.name}")

    def execute_mcp_tool(self, tool_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a tool through MCP if available"""
        if not self.mcp_host or not self.mcp_session_id:
            logger.error("MCP host or session not available")
            return {"status": "error", "message": "MCP not available"}

        return self.mcp_host.execute_tool(self.mcp_session_id, tool_id, parameters)

    def get_available_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools"""
        if not self.mcp_host or not self.mcp_session_id:
            logger.error("MCP host or session not available")
            return []

        return self.mcp_host.get_available_tools(self.mcp_session_id)

    def cleanup(self) -> None:
        """Clean up resources used by the agent"""
        if self.mcp_host and self.mcp_session_id:
            self.mcp_host.end_session(self.mcp_session_id)
            logger.info(f"MCP session ended for agent {self.agent_card.name}")