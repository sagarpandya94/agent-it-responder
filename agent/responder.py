import json
import logging
from openai import OpenAI

from tools import TOOL_REGISTRY, TOOLS_SCHEMA
from tools.escalate import escalate_to_engineer

logger = logging.getLogger(__name__)

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

# Safety ceiling: if the agent hasn't resolved the incident within this many
# LLM calls, we stop the loop and escalate rather than looping forever.
DEFAULT_MAX_TURNS = 10


class MaxTurnsExceededError(Exception):
    """Raised when the agent loop exceeds the maximum allowed turns."""


class ITResponderAgent:
    """
    Agentic loop that uses OpenAI function-calling to triage and resolve
    IT incidents autonomously.

    The agent will:
    1. Inspect server health and logs.
    2. Decide whether to restart the service or escalate to a human.
    3. Return a final natural-language summary of what it did.

    If the agent has not reached a conclusion within `max_turns` LLM calls,
    it force-escalates the incident rather than looping indefinitely.
    """

    def __init__(self, client: OpenAI, model: str = "gpt-4o", max_turns: int = DEFAULT_MAX_TURNS):
        self.client    = client
        self.model     = model
        self.max_turns = max_turns

    def run(self, user_issue: str) -> str:
        """
        Run the agent on a reported incident.

        Args:
            user_issue: Free-text description of the problem (e.g. from a user alert).

        Returns:
            The agent's final response as a string.

        Raises:
            MaxTurnsExceededError: If the agent exceeds max_turns without resolving.
                                   The incident is auto-escalated before raising.
        """
        logger.info("New incident received: %s", user_issue)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_issue},
        ]

        for turn in range(1, self.max_turns + 1):
            logger.debug("Agent turn %d / %d", turn, self.max_turns)

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

                    logger.info("Tool call: %s(%s)", func_name, func_args)

                    tool_fn = TOOL_REGISTRY.get(func_name)
                    if tool_fn is None:
                        logger.error("Unknown tool requested by agent: %s", func_name)
                        tool_output = json.dumps({"error": f"Unknown tool: {func_name}"})
                    else:
                        tool_output = tool_fn(**func_args)

                    logger.debug("Tool result for %s: %s", func_name, tool_output)

                    # Feed the tool result back into the conversation.
                    messages.append({
                        "role":         "tool",
                        "tool_call_id": tool_call.id,
                        "name":         func_name,
                        "content":      tool_output,
                    })

            # ── No more tool calls → agent has reached a conclusion ───────
            else:
                final_response = response_msg.content
                logger.info("Incident resolved after %d turn(s): %s", turn, final_response)
                return final_response

        # ── Max turns exceeded ────────────────────────────────────────────
        summary = (
            f"Agent exceeded {self.max_turns} turns without resolving: '{user_issue}'. "
            "Manual investigation required."
        )
        logger.error("Max turns (%d) exceeded. Force-escalating. Issue: %s", self.max_turns, user_issue)
        escalate_to_engineer(summary)

        raise MaxTurnsExceededError(summary)
