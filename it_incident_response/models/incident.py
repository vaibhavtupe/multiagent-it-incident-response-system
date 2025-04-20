import uuid
import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

from it_incident_response.simulation.incident_data import (
    get_random_incident, get_incident_by_index, SIMULATED_INCIDENTS
)

class IncidentSeverity(Enum):
    """Severity levels for IT incidents"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    """Possible statuses for an incident"""
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Incident:
    """Represents an IT incident"""

    def __init__(self, incident_id: str, title: str, description: str,
                 severity: IncidentSeverity, affected_systems: List[str],
                 tags: List[str] = None):
        self.incident_id = incident_id
        self.title = title
        self.description = description
        self.severity = severity
        self.affected_systems = affected_systems
        self.tags = tags or []
        self.status = IncidentStatus.INVESTIGATING
        self.reported_time = datetime.datetime.now().isoformat()
        self.updated_time = self.reported_time
        self.assigned_to = None
        self.notes = []

    def update_status(self, new_status: IncidentStatus, note: str = None) -> None:
        """Update the incident status"""
        self.status = new_status
        self.updated_time = datetime.datetime.now().isoformat()

        if note:
            self.add_note(note)

    def add_note(self, note: str) -> None:
        """Add a note to the incident"""
        self.notes.append({
            "content": note,
            "timestamp": datetime.datetime.now().isoformat()
        })
        self.updated_time = datetime.datetime.now().isoformat()

    def assign_to(self, assignee: str) -> None:
        """Assign the incident to someone"""
        self.assigned_to = assignee
        self.updated_time = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary representation"""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "affected_systems": self.affected_systems,
            "tags": self.tags,
            "status": self.status.value,
            "reported_time": self.reported_time,
            "updated_time": self.updated_time,
            "assigned_to": self.assigned_to,
            "notes": self.notes
        }

# Global incident store for the simulation
_incidents: Dict[str, Incident] = {}

def create_incident(title: str, description: str, severity: str,
                    affected_systems: List[str], tags: List[str] = None) -> str:
    """Create a new incident and store it"""
    incident_id = str(uuid.uuid4())

    # Convert string severity to enum
    try:
        severity_enum = IncidentSeverity(severity.lower())
    except ValueError:
        severity_enum = IncidentSeverity.MEDIUM

    incident = Incident(
        incident_id=incident_id,
        title=title,
        description=description,
        severity=severity_enum,
        affected_systems=affected_systems,
        tags=tags
    )

    _incidents[incident_id] = incident
    return incident_id

def get_incident_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
    """Get an incident by ID, returning its dictionary representation"""
    if incident_id in _incidents:
        return _incidents[incident_id].to_dict()
    return None

def update_incident_status(incident_id: str, status: str, note: str = None) -> bool:
    """Update the status of an incident"""
    if incident_id not in _incidents:
        return False

    # Convert string status to enum
    try:
        status_enum = IncidentStatus(status.lower())
    except ValueError:
        return False

    _incidents[incident_id].update_status(status_enum, note)
    return True

def assign_incident(incident_id: str, assignee: str) -> bool:
    """Assign an incident to someone"""
    if incident_id not in _incidents:
        return False

    _incidents[incident_id].assign_to(assignee)
    return True

def add_incident_note(incident_id: str, note: str) -> bool:
    """Add a note to an incident"""
    if incident_id not in _incidents:
        return False

    _incidents[incident_id].add_note(note)
    return True

def get_all_incidents() -> List[Dict[str, Any]]:
    """Get all incidents as dictionary representations"""
    return [incident.to_dict() for incident in _incidents.values()]

def load_simulated_incidents(count: int = 3) -> List[str]:
    """Load a number of simulated incidents into the system"""
    incident_ids = []

    # Load predefined incidents
    for i in range(min(count, len(SIMULATED_INCIDENTS))):
        incident_data = get_incident_by_index(i)
        incident_id = create_incident(
            title=incident_data["title"],
            description=incident_data["description"],
            severity=incident_data["severity"],
            affected_systems=incident_data["affected_systems"],
            tags=incident_data.get("tags", [])
        )
        incident_ids.append(incident_id)

    return incident_ids