from typing import List, Dict, Any
import datetime
import random

# Simulated system metrics for different system types
def generate_db_server_metrics(timestamp: datetime.datetime, server_id: str, is_problem: bool = False) -> Dict[str, Any]:
    """Generate simulated metrics for a database server"""
    cpu_usage = random.uniform(60, 90) if is_problem else random.uniform(20, 60)
    memory_usage = random.uniform(70, 95) if is_problem else random.uniform(40, 70)
    disk_io_wait = random.uniform(15, 40) if is_problem else random.uniform(5, 15)
    active_connections = random.randint(80, 150) if is_problem else random.randint(30, 80)
    connection_time_ms = random.uniform(500, 2000) if is_problem else random.uniform(10, 100)
    query_execution_time_ms = random.uniform(300, 1500) if is_problem else random.uniform(5, 50)

    return {
        "timestamp": timestamp.isoformat(),
        "server_id": server_id,
        "server_type": "database",
        "metrics": {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
            "disk_io_wait_percent": disk_io_wait,
            "active_connections": active_connections,
            "connection_time_ms": connection_time_ms,
            "query_execution_time_ms": query_execution_time_ms,
            "disk_free_gb": random.uniform(500, 2000),
            "network_latency_ms": random.uniform(60, 300) if is_problem else random.uniform(1, 10)
        }
    }

def generate_app_server_metrics(timestamp: datetime.datetime, server_id: str, is_problem: bool = False) -> Dict[str, Any]:
    """Generate simulated metrics for an application server"""
    cpu_usage = random.uniform(70, 95) if is_problem else random.uniform(30, 70)
    memory_usage = random.uniform(75, 95) if is_problem else random.uniform(50, 75)
    response_time_ms = random.uniform(500, 2000) if is_problem else random.uniform(50, 200)
    request_rate = random.uniform(100, 500) if is_problem else random.uniform(50, 300)
    error_rate = random.uniform(5, 20) if is_problem else random.uniform(0.1, 2)

    return {
        "timestamp": timestamp.isoformat(),
        "server_id": server_id,
        "server_type": "application",
        "metrics": {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
            "disk_usage_percent": random.uniform(40, 70),
            "response_time_ms": response_time_ms,
            "request_rate_per_minute": request_rate,
            "error_rate_percent": error_rate,
            "connection_pool_utilization_percent": random.uniform(70, 100) if is_problem else random.uniform(20, 70),
            "jvm_heap_usage_percent": random.uniform(80, 95) if is_problem else random.uniform(40, 80),
            "thread_count": random.randint(100, 300) if is_problem else random.randint(50, 150)
        }
    }

def generate_api_gateway_metrics(timestamp: datetime.datetime, server_id: str, is_problem: bool = False) -> Dict[str, Any]:
    """Generate simulated metrics for an API gateway"""
    request_rate = random.uniform(500, 2000)
    error_rate = random.uniform(10, 40) if is_problem else random.uniform(0.1, 2)
    upstream_latency = random.uniform(500, 3000) if is_problem else random.uniform(50, 200)

    return {
        "timestamp": timestamp.isoformat(),
        "server_id": server_id,
        "server_type": "api_gateway",
        "metrics": {
            "request_rate_per_minute": request_rate,
            "error_rate_percent": error_rate,
            "upstream_latency_ms": upstream_latency,
            "p95_response_time_ms": random.uniform(800, 5000) if is_problem else random.uniform(100, 500),
            "circuit_breakers_open": random.randint(1, 5) if is_problem else 0,
            "rate_limited_requests": random.randint(50, 200) if is_problem else random.randint(0, 20),
            "cpu_usage_percent": random.uniform(50, 90),
            "memory_usage_percent": random.uniform(40, 80)
        }
    }

def generate_storage_node_metrics(timestamp: datetime.datetime, server_id: str, is_problem: bool = False) -> Dict[str, Any]:
    """Generate simulated metrics for a storage node"""
    disk_usage = random.uniform(90, 99) if is_problem else random.uniform(60, 85)
    iops = random.uniform(1000, 5000)
    latency_ms = random.uniform(20, 100) if is_problem else random.uniform(1, 20)

    return {
        "timestamp": timestamp.isoformat(),
        "server_id": server_id,
        "server_type": "storage",
        "metrics": {
            "disk_usage_percent": disk_usage,
            "iops": iops,
            "disk_latency_ms": latency_ms,
            "read_throughput_mbps": random.uniform(100, 500),
            "write_throughput_mbps": random.uniform(50, 300),
            "cpu_usage_percent": random.uniform(20, 60),
            "memory_usage_percent": random.uniform(30, 70),
            "error_count": random.randint(10, 50) if is_problem else random.randint(0, 5)
        }
    }

def generate_network_metrics(timestamp: datetime.datetime, is_problem: bool = False) -> Dict[str, Any]:
    """Generate simulated network metrics between components"""
    baseline_latency = 2
    problem_factor = random.uniform(10, 50) if is_problem else 1

    return {
        "timestamp": timestamp.isoformat(),
        "metrics": {
            "app_to_db_latency_ms": baseline_latency * problem_factor,
            "app_to_api_latency_ms": baseline_latency * (problem_factor / 2 if is_problem else 1.2),
            "api_to_backend_latency_ms": baseline_latency * (problem_factor / 1.5 if is_problem else 1.1),
            "internet_to_app_latency_ms": baseline_latency * 2,
            "packet_loss_percent": random.uniform(2, 10) if is_problem else random.uniform(0, 0.5),
            "bandwidth_utilization_percent": random.uniform(70, 95) if is_problem else random.uniform(30, 70)
        }
    }

# Map of server types to metric generators
SERVER_METRIC_GENERATORS = {
    "app-server": generate_app_server_metrics,
    "db-server": generate_db_server_metrics,
    "api-gateway": generate_api_gateway_metrics,
    "storage-node": generate_storage_node_metrics
}

def generate_system_metrics_for_incident(incident_data: Dict[str, Any],
                                         timestamp: datetime.datetime = None) -> List[Dict[str, Any]]:
    """Generate system metrics relevant to the incident"""
    if timestamp is None:
        timestamp = datetime.datetime.now()

    affected_systems = incident_data.get("affected_systems", [])
    metrics = []

    # Determine if this incident is causing network issues
    network_problem = any(tag in ["connectivity", "network", "latency"]
                          for tag in incident_data.get("tags", []))

    # Add network metrics if relevant
    if network_problem:
        metrics.append(generate_network_metrics(timestamp, is_problem=True))

    # Add server-specific metrics
    for system in affected_systems:
        server_type = None
        for type_prefix in SERVER_METRIC_GENERATORS.keys():
            if system.startswith(type_prefix):
                server_type = type_prefix
                break

        if server_type:
            generator = SERVER_METRIC_GENERATORS[server_type]
            # Generate a series of metrics over time
            for i in range(5):
                time_offset = datetime.timedelta(minutes=i*5)
                metrics.append(generator(timestamp - time_offset, system, is_problem=True))

    # Add some metrics for non-affected systems for comparison
    for server_type, generator in SERVER_METRIC_GENERATORS.items():
        sample_server = f"{server_type}-sample"
        if not any(system.startswith(server_type) for system in affected_systems):
            metrics.append(generator(timestamp, sample_server, is_problem=False))

    return metrics
