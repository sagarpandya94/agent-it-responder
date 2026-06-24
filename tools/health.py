import json
import logging

logger = logging.getLogger(__name__)

# Mock metrics for servers the agent manages.
# For "localhost", psutil is used to return real machine metrics.
MOCK_SERVER_METRICS = {
    "payment-server-01": {"cpu": "98%", "memory": "40%", "status": "Warning"},
    "db-node-02":        {"cpu": "12%", "memory": "60%", "status": "Healthy"},
    "auth-service-03":   {"cpu": "45%", "memory": "95%", "status": "Critical"},
    "search-index-09":   {"cpu": "10%", "memory": "15%", "status": "Error"},
    "frontend-node-04":  {"cpu": "25%", "memory": "30%", "status": "Healthy"},
}


def _get_status(cpu_pct: float, memory_pct: float) -> str:
    """Derive a status label from raw metric percentages."""
    if cpu_pct > 90 or memory_pct > 90:
        return "Critical"
    if cpu_pct > 70 or memory_pct > 70:
        return "Warning"
    return "Healthy"


def get_server_health(server_id: str) -> str:
    """
    Returns CPU and memory usage for a given server as a JSON string.

    For 'localhost', psutil is used to fetch real metrics from this machine.
    All other server IDs fall back to the mock database.
    """
    logger.info("Checking health for server: %s", server_id)

    if server_id == "localhost":
        try:
            import psutil
            cpu_pct    = psutil.cpu_percent(interval=1)
            memory_pct = psutil.virtual_memory().percent
            result = {
                "cpu":    f"{cpu_pct:.1f}%",
                "memory": f"{memory_pct:.1f}%",
                "status": _get_status(cpu_pct, memory_pct),
                "source": "live",
            }
            logger.debug("Live metrics for localhost: %s", result)
        except ImportError:
            logger.warning("psutil not installed — falling back to mock data for localhost")
            result = {"error": "psutil not installed. Run: pip install psutil"}
    else:
        result = MOCK_SERVER_METRICS.get(
            server_id,
            {"error": f"Server '{server_id}' not found. Check the ID."},
        )
        logger.debug("Mock metrics for %s: %s", server_id, result)

    return json.dumps(result)
