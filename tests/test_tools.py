"""
Unit tests for individual tool functions.
These tests run entirely offline — no OpenAI API key required.
"""

import json
import pytest

from tools.health import get_server_health
from tools.logs import fetch_recent_logs
from tools.restart import restart_service
from tools.escalate import escalate_to_engineer


# ── get_server_health ─────────────────────────────────────────────────────────

class TestGetServerHealth:
    def test_known_server_returns_json(self):
        result = json.loads(get_server_health("payment-server-01"))
        assert "cpu" in result
        assert "memory" in result
        assert "status" in result

    def test_high_cpu_server(self):
        result = json.loads(get_server_health("payment-server-01"))
        assert result["status"] == "Warning"
        assert result["cpu"] == "98%"

    def test_healthy_server(self):
        result = json.loads(get_server_health("db-node-02"))
        assert result["status"] == "Healthy"

    def test_unknown_server_returns_error(self):
        result = json.loads(get_server_health("nonexistent-server-99"))
        assert "error" in result

    def test_localhost_returns_live_metrics(self):
        """psutil path: localhost should return real CPU/memory figures."""
        pytest.importorskip("psutil")   # skip gracefully if psutil not installed
        result = json.loads(get_server_health("localhost"))
        # Should not be an error
        assert "error" not in result
        assert "cpu" in result
        assert "memory" in result
        assert result.get("source") == "live"

    def test_localhost_cpu_is_valid_percentage(self):
        """Live CPU reading should be a parseable float between 0 and 100."""
        pytest.importorskip("psutil")
        result = json.loads(get_server_health("localhost"))
        if "error" in result:
            pytest.skip("psutil not available")
        cpu_value = float(result["cpu"].rstrip("%"))
        assert 0.0 <= cpu_value <= 100.0

    def test_localhost_memory_is_valid_percentage(self):
        """Live memory reading should be a parseable float between 0 and 100."""
        pytest.importorskip("psutil")
        result = json.loads(get_server_health("localhost"))
        if "error" in result:
            pytest.skip("psutil not available")
        mem_value = float(result["memory"].rstrip("%"))
        assert 0.0 <= mem_value <= 100.0


# ── fetch_recent_logs ─────────────────────────────────────────────────────────

class TestFetchRecentLogs:
    def test_returns_list_of_logs(self):
        result = json.loads(fetch_recent_logs("payment-server-01"))
        assert "logs" in result
        assert isinstance(result["logs"], list)

    def test_respects_line_limit(self):
        result = json.loads(fetch_recent_logs("payment-server-01", lines=3))
        assert len(result["logs"]) == 3

    def test_unknown_server_returns_defaults(self):
        result = json.loads(fetch_recent_logs("ghost-server-00"))
        assert len(result["logs"]) > 0

    def test_critical_logs_present_for_high_cpu_server(self):
        result = json.loads(fetch_recent_logs("payment-server-01"))
        combined = " ".join(result["logs"])
        assert "WARN" in combined or "CRITICAL" in combined or "ERROR" in combined


# ── restart_service ───────────────────────────────────────────────────────────

class TestRestartService:
    def test_returns_success_status(self):
        result = json.loads(restart_service("payment-server-01"))
        assert result["status"] == "success"

    def test_message_contains_server_id(self):
        result = json.loads(restart_service("auth-service-03"))
        assert "auth-service-03" in result["message"]


# ── escalate_to_engineer ──────────────────────────────────────────────────────

class TestEscalateToEngineer:
    def test_returns_escalated_status(self):
        result = json.loads(escalate_to_engineer("Search engine is down."))
        assert result["status"] == "escalated"

    def test_summary_echoed_in_response(self):
        summary = "Connection refused on elastic-cluster-main:9200"
        result = json.loads(escalate_to_engineer(summary))
        assert result["summary"] == summary
