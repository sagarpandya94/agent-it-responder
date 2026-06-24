import json

# Mock log database keyed by server ID
LOG_DATABASE = {
    "payment-server-01": [
        "[INFO] Request received /pay/v1",
        "[WARN] CPU threshold exceeded 90%",
        "[WARN] Thread pool exhaustion",
        "[CRITICAL] Process hung, not accepting new connections",
        "[ERROR] Timeout waiting for thread",
    ],
    "db-node-02": [
        "[INFO] Backup started",
        "[INFO] Backup completed successfully",
        "[INFO] User query executed in 12ms",
        "[INFO] Health check: OK",
        "[INFO] Replication sync active",
    ],
    "auth-service-03": [
        "[INFO] Token validated user_882",
        "[WARN] Garbage collection taking too long (>5s)",
        "[ERROR] java.lang.OutOfMemoryError: Java heap space",
        "[CRITICAL] Application crashing due to memory leak",
        "[INFO] Restarting context...",
    ],
    "search-index-09": [
        "[INFO] Indexing started",
        "[ERROR] Connection refused: elastic-cluster-main:9200",
        "[ERROR] Failed to write document ID 4432",
        "[CRITICAL] Dependency Unreachable: Search Engine is down",
        "[ERROR] Retrying in 30s...",
    ],
    "frontend-node-04": [
        "[INFO] GET /home 200 OK",
        "[INFO] GET /assets/logo.png 200 OK",
        "[INFO] GET /login 200 OK",
        "[INFO] GET /api/v1/status 200 OK",
        "[INFO] Health check passed",
    ],
}

DEFAULT_LOGS = [
    "[INFO] System stable",
    "[INFO] Heartbeat signal received",
]


def fetch_recent_logs(server_id: str, lines: int = 5) -> str:
    """Returns the last N log lines for a given server as a JSON string."""
    print(f"-> TOOL: Fetching last {lines} log lines for {server_id}...")
    logs = LOG_DATABASE.get(server_id, DEFAULT_LOGS)
    return json.dumps({"logs": logs[:lines]})
