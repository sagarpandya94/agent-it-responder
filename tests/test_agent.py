"""
Unit tests for the ITResponderAgent loop logic.
Uses mocking so no OpenAI API key is required.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, call

from agent.responder import ITResponderAgent, MaxTurnsExceededError


def _make_text_response(content: str):
    """Build a mock OpenAI response with no tool calls (final answer)."""
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = None
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_tool_response(tool_name: str, tool_args: dict, tool_call_id: str = "call_001"):
    """Build a mock OpenAI response that requests a single tool call."""
    tool_call = MagicMock()
    tool_call.id = tool_call_id
    tool_call.function.name = tool_name
    tool_call.function.arguments = json.dumps(tool_args)

    msg = MagicMock()
    msg.content = None
    msg.tool_calls = [tool_call]
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


class TestITResponderAgentLoop:
    def setup_method(self):
        self.client = MagicMock()
        self.agent  = ITResponderAgent(client=self.client, model="gpt-4o", max_turns=5)

    def test_resolves_immediately_with_no_tool_calls(self):
        """If the LLM answers directly, run() returns that answer."""
        self.client.chat.completions.create.return_value = _make_text_response(
            "Server looks healthy, no action needed."
        )
        result = self.agent.run("Is frontend-node-04 OK?")
        assert result == "Server looks healthy, no action needed."
        assert self.client.chat.completions.create.call_count == 1

    def test_calls_tool_then_resolves(self):
        """Agent calls one tool, gets a result, then gives a final answer."""
        self.client.chat.completions.create.side_effect = [
            _make_tool_response("get_server_health", {"server_id": "db-node-02"}),
            _make_text_response("DB node is healthy. No action required."),
        ]

        with patch("tools.health.get_server_health", return_value='{"cpu":"12%","memory":"60%","status":"Healthy"}'):
            result = self.agent.run("Check db-node-02")

        assert "healthy" in result.lower()
        assert self.client.chat.completions.create.call_count == 2

    def test_raises_on_max_turns_exceeded(self):
        """Agent should raise MaxTurnsExceededError if it never stops calling tools."""
        # Always return a tool call → loop never terminates naturally
        self.client.chat.completions.create.return_value = _make_tool_response(
            "get_server_health", {"server_id": "payment-server-01"}
        )

        with patch("tools.health.get_server_health", return_value='{"cpu":"98%","memory":"40%","status":"Warning"}'), \
             patch("agent.responder.escalate_to_engineer") as mock_escalate:

            mock_escalate.return_value = '{"status":"escalated"}'

            with pytest.raises(MaxTurnsExceededError):
                self.agent.run("payment-server-01 is slow")

            # Should have called escalate as a safety net
            mock_escalate.assert_called_once()
            # Should have run exactly max_turns times
            assert self.client.chat.completions.create.call_count == self.agent.max_turns

    def test_max_turns_error_message_contains_issue(self):
        """The MaxTurnsExceededError message should reference the original issue."""
        self.client.chat.completions.create.return_value = _make_tool_response(
            "get_server_health", {"server_id": "payment-server-01"}
        )

        with patch("tools.health.get_server_health", return_value='{"cpu":"98%"}'), \
             patch("agent.responder.escalate_to_engineer", return_value='{"status":"escalated"}'):

            with pytest.raises(MaxTurnsExceededError) as exc_info:
                self.agent.run("payment-server-01 is timing out")

            assert "payment-server-01 is timing out" in str(exc_info.value)
