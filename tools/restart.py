import json


def restart_service(server_id: str) -> str:
    """
    Simulates restarting a service on the given server.
    The AI decides when to call this (CPU or memory > 90%).
    Returns a JSON string confirming the restart.
    """
    print(f"-> TOOL: Restarting service for {server_id}...")
    return json.dumps({
        "status": "success",
        "message": f"Service on {server_id} restarted successfully.",
    })
