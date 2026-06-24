import json
from openai import OpenAI

from tools import TOOL_REGISTRY, TOOLS_SCHEMA

SYSTEM_PROMPT = (
    "You are a Level 1 IT Incident Responder. Your job is to investigate server "
    "issues reported by users and take the appropriate automated action.\n\n"
    "Decision rules:\n"
    "- Always start by checking server health AND fetching recent logs.\n"
    "- If CPU or Memory is above 90%, restart the service.\n"
    "- If logs show a critical dependency failure (e.g. 'Connection refused', "
    "'Dependency Unreachable') that a restart will NOT fix, escalate to an engineer.\n"
    "- If the server is healthy and logs look normal, report that no action is needed."
)


class ITResponderAgent:
    """
    Agentic loop that uses OpenAI function-calling to triage and resolve
    IT incidents autonomously.

    The agent will:
    1. Inspect server health and logs.
    2. Decide whether to restart the service or escalate to a human.
    3. Return a final natural-language summary of what it did.
    """

    def __init__(self, client: OpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model

    def run(self, user_issue: str) -> str:
        """
        Run the agent on a reported incident.

        Args:
            user_issue: Free-text description of the problem (e.g. from a user alert).

        Returns:
            The agent's final response as a string.
        """
        print(f"\n{'='*60}")
        print(f"  NEW INCIDENT: {user_issue}")
        print(f"{'='*60}")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_issue},
        ]

        while True:
            print("\n[AI Thinking...]")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )

            response_msg = response.choices[0].message
            messages.append(response_msg)

            # ── Tool calls requested ──────────────────────────────────────
            if response_msg.tool_calls:
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    tool_fn = TOOL_REGISTRY.get(func_name)
                    if tool_fn is None:
                        tool_output = json.dumps({"error": f"Unknown tool: {func_name}"})
                    else:
                        tool_output = tool_fn(**func_args)

                    # Feed the tool result back into the conversation.
                    messages.append({
                        "role":         "tool",
                        "tool_call_id": tool_call.id,
                        "name":         func_name,
                        "content":      tool_output,
                    })

            # ── No more tool calls → agent is done ───────────────────────
            else:
                final_response = response_msg.content
                print(f"\n[RESOLUTION]: {final_response}\n")
                return final_response
