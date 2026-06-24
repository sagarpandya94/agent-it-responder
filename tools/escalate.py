import json


def escalate_to_engineer(summary: str) -> str:
    """
    Escalates an incident to a human engineer by creating a support ticket.
    The AI calls this when the issue is too complex for automated remediation
    (e.g. dependency failures that a restart cannot fix).
    Returns a JSON string confirming the escalation.
    """
    print(f"-> TOOL: Escalating to human engineer...")
    print(f"   Summary: {summary}")
    return json.dumps({
        "status": "escalated",
        "message": "Incident ticket created and assigned to on-call engineer.",
        "summary": summary,
    })
