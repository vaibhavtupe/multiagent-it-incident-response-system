import uuid
import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

class DiagnosticStatus(Enum):
    """Status of a diagnostic analysis"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DiagnosticReport:
    """Represents a diagnostic analysis report for an incident"""

    def __init__(self, report_id: str, incident_id: str):
        self.report_id = report_id
        self.incident_id = incident_id
        self.status = DiagnosticStatus.PENDING
        self.created_time = datetime.datetime.now().isoformat()
        self.updated_time = self.created_time
        self.completed_time = None
        self.root_cause = None
        self.confidence = None
        self.evidence = []
        self.recommended_actions = []
        self.knowledge_base_references = []

    def update_status(self, new_status: DiagnosticStatus) -> None:
        """Update the analysis status"""
        self.status = new_status
        self.updated_time = datetime.datetime.now().isoformat()

        if new_status == DiagnosticStatus.COMPLETED:
            self.completed_time = self.updated_time

    def set_root_cause(self, root_cause: str, confidence: float) -> None:
        """Set the identified root cause and confidence level"""
        self.root_cause = root_cause
        self.confidence = confidence
        self.updated_time = datetime.datetime.now().isoformat()

    def add_evidence(self, evidence: str) -> None:
        """Add a piece of evidence supporting the diagnosis"""
        self.evidence.append(evidence)
        self.updated_time = datetime.datetime.now().isoformat()

    def add_recommended_action(self, action: str) -> None:
        """Add a recommended action to resolve the incident"""
        self.recommended_actions.append(action)
        self.updated_time = datetime.datetime.now().isoformat()

    def add_knowledge_base_reference(self, reference: Dict[str, Any]) -> None:
        """Add a reference to a knowledge base article"""
        self.knowledge_base_references.append(reference)
        self.updated_time = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostic report to dictionary representation"""
        return {
            "report_id": self.report_id,
            "incident_id": self.incident_id,
            "status": self.status.value,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "completed_time": self.completed_time,
            "root_cause": self.root_cause,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "recommended_actions": self.recommended_actions,
            "knowledge_base_references": self.knowledge_base_references
        }

# Global diagnostic report store for the simulation
_diagnostic_reports: Dict[str, DiagnosticReport] = {}

def create_diagnostic_report(incident_id: str) -> str:
    """Create a new diagnostic report for an incident"""
    report_id = str(uuid.uuid4())
    report = DiagnosticReport(report_id=report_id, incident_id=incident_id)
    _diagnostic_reports[report_id] = report
    return report_id

def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Get a diagnostic report by ID, returning its dictionary representation"""
    if report_id in _diagnostic_reports:
        return _diagnostic_reports[report_id].to_dict()
    return None

def get_report_by_incident_id(incident_id: str) -> Optional[Dict[str, Any]]:
    """Get a diagnostic report by incident ID, returning its dictionary representation"""
    for report in _diagnostic_reports.values():
        if report.incident_id == incident_id:
            return report.to_dict()
    return None

def update_report_status(report_id: str, status: str) -> bool:
    """Update the status of a diagnostic report"""
    if report_id not in _diagnostic_reports:
        return False

    # Convert string status to enum
    try:
        status_enum = DiagnosticStatus(status.lower())
    except ValueError:
        return False

    _diagnostic_reports[report_id].update_status(status_enum)
    return True

def set_report_root_cause(report_id: str, root_cause: str, confidence: float) -> bool:
    """Set the root cause for a diagnostic report"""
    if report_id not in _diagnostic_reports:
        return False

    _diagnostic_reports[report_id].set_root_cause(root_cause, confidence)
    return True

def add_report_evidence(report_id: str, evidence: str) -> bool:
    """Add evidence to a diagnostic report"""
    if report_id not in _diagnostic_reports:
        return False

    _diagnostic_reports[report_id].add_evidence(evidence)
    return True

def add_report_action(report_id: str, action: str) -> bool:
    """Add a recommended action to a diagnostic report"""
    if report_id not in _diagnostic_reports:
        return False

    _diagnostic_reports[report_id].add_recommended_action(action)
    return True

def add_report_reference(report_id: str, reference: Dict[str, Any]) -> bool:
    """Add a knowledge base reference to a diagnostic report"""
    if report_id not in _diagnostic_reports:
        return False

    _diagnostic_reports[report_id].add_knowledge_base_reference(reference)
    return True