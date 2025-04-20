import uuid
import json
import logging
import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

logger = logging.getLogger("it-incident-response.a2a")

class PartType(Enum):
    """Types of content parts in A2A messages"""
    TEXT = "text/plain"
    JSON = "application/json"
    FILE = "application/octet-stream"
    HTML = "text/html"

@dataclass
class AgentCapability:
    """Capability advertised by an agent"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentCard:
    """Agent Card as defined in the A2A protocol"""
    agent_id: str
    name: str
    description: str
    version: str
    base_url: str
    capabilities: List[AgentCapability] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "base_url": self.base_url,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "parameters": cap.parameters
                }
                for cap in self.capabilities
            ]
        }

@dataclass
class MessagePart:
    """A part within an A2A message"""
    part_id: str
    content_type: PartType
    content: Any

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization"""
        return {
            "part_id": self.part_id,
            "content_type": self.content_type.value,
            "content": self.content
        }

@dataclass
class A2AMessage:
    """A message in the A2A protocol"""
    message_id: str
    role: str  # "user" or "agent"
    parts: List[MessagePart] = field(default_factory=list)

    def add_text_part(self, text: str) -> str:
        """Add a text part to the message and return its ID"""
        part_id = str(uuid.uuid4())
        self.parts.append(
            MessagePart(
                part_id=part_id,
                content_type=PartType.TEXT,
                content=text
            )
        )
        return part_id

    def add_json_part(self, data: Dict[str, Any]) -> str:
        """Add a JSON part to the message and return its ID"""
        part_id = str(uuid.uuid4())
        self.parts.append(
            MessagePart(
                part_id=part_id,
                content_type=PartType.JSON,
                content=data
            )
        )
        return part_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization"""
        return {
            "message_id": self.message_id,
            "role": self.role,
            "parts": [part.to_dict() for part in self.parts]
        }

class TaskState(Enum):
    """States for an A2A task"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

@dataclass
class A2ATask:
    """A task in the A2A protocol"""
    task_id: str
    state: TaskState
    messages: List[A2AMessage] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    def add_message(self, message: A2AMessage) -> None:
        """Add a message to the task"""
        self.messages.append(message)
        self.updated_at = datetime.datetime.now().isoformat()

    def update_state(self, new_state: TaskState) -> None:
        """Update the task state"""
        self.state = new_state
        self.updated_at = datetime.datetime.now().isoformat()

    def add_artifact(self, artifact_id: str, name: str, parts: List[MessagePart]) -> None:
        """Add an artifact to the task"""
        self.artifacts.append({
            "artifact_id": artifact_id,
            "name": name,
            "parts": [part.to_dict() for part in parts]
        })
        self.updated_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization"""
        return {
            "task_id": self.task_id,
            "state": self.state.value,
            "messages": [msg.to_dict() for msg in self.messages],
            "artifacts": self.artifacts,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }