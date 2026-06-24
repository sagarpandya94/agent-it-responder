from tools.health import get_server_health
from tools.logs import fetch_recent_logs
from tools.restart import restart_service
from tools.escalate import escalate_to_engineer

# Maps tool names (as the LLM knows them) to their Python implementations.
TOOL_REGISTRY = {
    "get_server_health": get_server_health,
    "fetch_recent_logs": fetch_recent_logs,
    "restart_service": restart_service,
    "escalate_to_engineer": escalate_to_engineer,
}

# OpenAI function-calling schema sent with every API request.
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_server_health",
            "description": (
                "Checks the current CPU and memory usage of a specific server "
                "and returns its health status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "The unique server identifier, e.g. 'payment-server-01'.",
                    }
                },
                "required": ["server_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_recent_logs",
            "description": (
                "Retrieves the most recent log entries from a server "
                "to help diagnose errors or anomalies."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "The unique server identifier.",
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of recent log lines to retrieve (default 5).",
                    },
                },
                "required": ["server_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "restart_service",
            "description": (
                "Restarts the service running on the specified server. "
                "Use this when CPU or memory usage exceeds 90%."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "The unique server identifier.",
                    }
                },
                "required": ["server_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_engineer",
            "description": (
                "Escalates the incident to a human on-call engineer. "
                "Use this when the issue cannot be fixed automatically "
                "(e.g. dependency failures, unknown errors)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": (
                            "A concise description of the problem and any "
                            "diagnostic findings gathered so far."
                        ),
                    }
                },
                "required": ["summary"],
            },
        },
    },
]
