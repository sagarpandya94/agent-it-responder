import json
import logging

logger = logging.getLogger(__name__)


def restart_service(server_id: str) -> str:
    """
    Simulates restarting a service on the given server.
    The AI decides when to call this (CPU or memory > 90%).
    Returns a JSON string confirming the restart.
    """
    logger.info("Restarting service on server: %s", server_id)
    result = {
        "status": "success",
        "message": f"Service on {server_id} restarted successfully.",
    }
    logger.debug("Restart result: %s", result)
    return json.dumps(result)
