# Each scenario describes what user input to send and what the agent should do.
# Used by both the demo runner and the unit tests.

SCENARIOS = [
    {
        "id": "A",
        "description": "High CPU — should trigger a restart",
        "user_issue": "The payment-server-01 is extremely slow and timing out.",
        "expected_action": "restart_service",
    },
    {
        "id": "B",
        "description": "Healthy DB — should report no action needed",
        "user_issue": "Something is wrong with db-node-02",
        "expected_action": "none",
    },
    {
        "id": "C",
        "description": "High memory / OOM — should trigger a restart",
        "user_issue": "Users are reporting login failures on auth-service-03.",
        "expected_action": "restart_service",
    },
    {
        "id": "D",
        "description": "Dependency failure — should escalate to engineer",
        "user_issue": "Search isn't working. Can you check search-index-09?",
        "expected_action": "escalate_to_engineer",
    },
    {
        "id": "E",
        "description": "Healthy server — should report all clear",
        "user_issue": "Check frontend-node-04 just to be safe.",
        "expected_action": "none",
    },
]
