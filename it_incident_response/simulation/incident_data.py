import datetime
from typing import List, Dict, Any

# Predefined incidents for simulation
SIMULATED_INCIDENTS = [
    {
        "title": "Database connectivity issues in production",
        "description": "Users reporting slow response times and intermittent errors when accessing customer data. Multiple timeouts observed in application logs.",
        "severity": "high",
        "affected_systems": ["app-server-01", "db-server-02"],
        "tags": ["database", "connectivity", "timeout"]
    },
    {
        "title": "API Gateway returning 503 errors",
        "description": "External API calls failing with 503 Service Unavailable errors. Approximately 15% of requests affected.",
        "severity": "critical",
        "affected_systems": ["api-gateway-prod", "load-balancer-01"],
        "tags": ["api", "gateway", "503", "availability"]
    },
    {
        "title": "Memory leak in authentication service",
        "description": "Authentication service memory usage increasing steadily over time, requiring frequent restarts.",
        "severity": "medium",
        "affected_systems": ["auth-service-01", "auth-service-02"],
        "tags": ["memory", "leak", "authentication"]
    },
    {
        "title": "Disk space critical on storage cluster",
        "description": "Storage cluster reporting 95% disk usage, approaching critical threshold.",
        "severity": "high",
        "affected_systems": ["storage-node-03", "storage-node-04"],
        "tags": ["storage", "disk", "space"]
    },
    {
        "title": "SSL certificate expiration warning",
        "description": "SSL certificate for customer portal will expire in 7 days.",
        "severity": "low",
        "affected_systems": ["customer-portal"],
        "tags": ["ssl", "certificate", "expiration"]
    }
]

def get_random_incident() -> Dict[str, Any]:
    """Return a random predefined incident"""
    import random
    return random.choice(SIMULATED_INCIDENTS)

def get_incident_by_index(index: int) -> Dict[str, Any]:
    """Return a specific incident by index"""
    if 0 <= index < len(SIMULATED_INCIDENTS):
        return SIMULATED_INCIDENTS[index]
    return SIMULATED_INCIDENTS[0]  # Default to first incident if index out of range
