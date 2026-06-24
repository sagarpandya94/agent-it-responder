import json

# Mock server metrics database
SERVER_METRICS = {
    "payment-server-01": {"cpu": "98%", "memory": "40%", "status": "Warning"},
    "db-node-02":        {"cpu": "12%", "memory": "60%", "status": "Healthy"},
    "auth-service-03":   {"cpu": "45%", "memory": "95%", "status": "Critical"},
    "search-index-09":   {"cpu": "10%", "memory": "15%", "status": "Error"},
    "frontend-node-04":  {"cpu": "25%", "memory": "30%", "status": "Healthy"},
}


def get_server_health(server_id: str) -> str:
    """Returns CPU and memory usage for a given server as a JSON string."""
    print(f"-> TOOL: Checking health for {server_id}...")
    result = SERVER_METRICS.get(server_id, {"error": "Server not found. Check the ID."})
    return json.dumps(result)
