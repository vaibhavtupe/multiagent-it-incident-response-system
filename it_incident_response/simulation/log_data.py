import datetime
from typing import List, Dict, Any

# Simulated log data for different incident types
DATABASE_CONNECTIVITY_LOGS = [
    {"timestamp": "2025-04-18T14:32:15.032Z", "level": "ERROR", "service": "customer-api", "message": "Database connection timeout after 10000ms"},
    {"timestamp": "2025-04-18T14:32:18.107Z", "level": "ERROR", "service": "customer-api", "message": "Failed to execute query: Connection terminated unexpectedly"},
    {"timestamp": "2025-04-18T14:33:05.724Z", "level": "ERROR", "service": "inventory-service", "message": "Database connection timeout after 10000ms"},
    {"timestamp": "2025-04-18T14:33:07.892Z", "level": "WARN", "service": "connection-pool", "message": "Connection pool exhausted, waiting for available connection"},
    {"timestamp": "2025-04-18T14:33:10.513Z", "level": "ERROR", "service": "customer-api", "message": "Database connection timeout after 10000ms"},
    {"timestamp": "2025-04-18T14:33:25.416Z", "level": "ERROR", "service": "order-processing", "message": "Failed to retrieve order data: database connection error"},
    {"timestamp": "2025-04-18T14:33:28.127Z", "level": "ERROR", "service": "inventory-service", "message": "Database connection timeout after 10000ms"},
    {"timestamp": "2025-04-18T14:34:01.982Z", "level": "WARN", "service": "system-monitor", "message": "Detected network latency spike between app and database servers"},
    {"timestamp": "2025-04-18T14:34:15.073Z", "level": "INFO", "service": "connection-pool", "message": "Retrying database connection with exponential backoff"}
]

API_GATEWAY_LOGS = [
    {"timestamp": "2025-04-18T09:15:23.107Z", "level": "ERROR", "service": "api-gateway", "message": "Upstream service returned 503 Service Unavailable"},
    {"timestamp": "2025-04-18T09:15:28.214Z", "level": "ERROR", "service": "api-gateway", "message": "Circuit breaker triggered for payment-service endpoint"},
    {"timestamp": "2025-04-18T09:16:05.392Z", "level": "WARN", "service": "load-balancer", "message": "Backend service health check failed for instance payment-service-03"},
    {"timestamp": "2025-04-18T09:17:12.486Z", "level": "ERROR", "service": "api-gateway", "message": "Upstream service returned 503 Service Unavailable"},
    {"timestamp": "2025-04-18T09:18:03.512Z", "level": "ERROR", "service": "monitoring", "message": "Multiple API endpoints returning errors, possible service degradation"}
]

MEMORY_LEAK_LOGS = [
    {"timestamp": "2025-04-18T22:05:12.513Z", "level": "WARN", "service": "auth-service-01", "message": "Memory usage at 85% and increasing steadily"},
    {"timestamp": "2025-04-18T22:35:45.716Z", "level": "WARN", "service": "auth-service-01", "message": "Memory usage at 90% and increasing steadily"},
    {"timestamp": "2025-04-18T23:05:32.892Z", "level": "ERROR", "service": "auth-service-01", "message": "Out of memory error in session management module"},
    {"timestamp": "2025-04-18T23:05:40.123Z", "level": "INFO", "service": "auth-service-01", "message": "Service restarting due to resource constraints"},
    {"timestamp": "2025-04-18T23:15:15.423Z", "level": "WARN", "service": "auth-service-01", "message": "Memory usage at 60% and increasing steadily"}
]

DISK_SPACE_LOGS = [
    {"timestamp": "2025-04-18T16:10:23.513Z", "level": "WARN", "service": "storage-monitor", "message": "Disk usage on storage-node-03 at 90%"},
    {"timestamp": "2025-04-18T17:25:15.127Z", "level": "WARN", "service": "storage-monitor", "message": "Disk usage on storage-node-03 at 92%"},
    {"timestamp": "2025-04-18T18:30:42.892Z", "level": "WARN", "service": "storage-monitor", "message": "Disk usage on storage-node-03 at 95%"},
    {"timestamp": "2025-04-18T18:32:15.416Z", "level": "WARN", "service": "storage-monitor", "message": "Disk usage on storage-node-04 at 93%"},
    {"timestamp": "2025-04-18T18:45:10.513Z", "level": "ERROR", "service": "backup-service", "message": "Scheduled backup failed: insufficient disk space"}
]

SSL_CERTIFICATE_LOGS = [
    {"timestamp": "2025-04-18T08:00:05.123Z", "level": "WARN", "service": "certificate-monitor", "message": "SSL certificate for customer-portal expires in 7 days"},
    {"timestamp": "2025-04-18T08:00:06.257Z", "level": "INFO", "service": "certificate-monitor", "message": "Automatic renewal attempted but failed: authorization error"},
    {"timestamp": "2025-04-18T09:15:30.513Z", "level": "INFO", "service": "helpdesk", "message": "Incident created for SSL certificate renewal"}
]

# Map incident types to log data
INCIDENT_LOGS_MAP = {
    "database": DATABASE_CONNECTIVITY_LOGS,
    "api": API_GATEWAY_LOGS,
    "memory": MEMORY_LEAK_LOGS,
    "disk": DISK_SPACE_LOGS,
    "ssl": SSL_CERTIFICATE_LOGS
}

def get_logs_for_incident(incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return simulated logs relevant to the given incident"""
    for tag in incident_data.get("tags", []):
        if tag in INCIDENT_LOGS_MAP:
            return INCIDENT_LOGS_MAP[tag]
    # Default to database logs if no matching tag
    return DATABASE_CONNECTIVITY_LOGS
