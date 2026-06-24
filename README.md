# 🤖 Agent IT Responder

[![CI](https://github.com/sagarpandya94/agent-it-responder/actions/workflows/ci.yml/badge.svg)](https://github.com/sagarpandya94/agent-it-responder/actions/workflows/ci.yml)

An autonomous IT incident response agent powered by OpenAI function-calling.
The agent investigates server health, reads logs, and takes action — restarting services or escalating to a human engineer — all without manual intervention.

---

## How It Works

The agent follows an **agentic loop** with a built-in safety ceiling:

```
User reports an incident
        ↓
  Agent checks health + logs   ←──────────────────────┐
        ↓                                             │
  AI decides next action                             │  (up to max_turns)
        ↓                                             │
  ┌─────────────┬──────────────────┬──────────────┐  │
  │ CPU/Mem>90% │ Dependency error │   Neither?   │  │
  ↓             ↓                  ↓              ↓  │
Restart      Escalate        Report healthy    (loop)─┘
                                    ↓
                            MaxTurnsExceededError
                            → force escalate
```

The LLM is given a system prompt with decision rules, a set of tools it can call, and the full conversation history. It keeps calling tools until it resolves or escalates the incident. If it hasn't concluded within `max_turns` (default: 10), the agent force-escalates and raises `MaxTurnsExceededError` — no infinite loops.

---

## Project Structure

```
agent-it-responder/
│
├── main.py                      # Entry point — runs all demo scenarios
│
├── agent/
│   ├── __init__.py
│   ├── responder.py             # ITResponderAgent class (agentic loop + max turns guard)
│   └── logging_config.py       # Centralised logging setup
│
├── tools/
│   ├── __init__.py              # Tool registry + OpenAI function-calling schema
│   ├── health.py                # get_server_health() — uses psutil for localhost
│   ├── logs.py                  # fetch_recent_logs()
│   ├── restart.py               # restart_service()
│   └── escalate.py              # escalate_to_engineer()
│
├── data/
│   └── scenarios.py             # Demo scenarios (used by main.py and tests)
│
├── tests/
│   ├── __init__.py
│   ├── test_tools.py            # Unit tests for tool functions (no API needed)
│   └── test_agent.py            # Unit tests for agent loop logic (mocked LLM)
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions — runs tests on every push
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Features

| Feature | Detail |
|---------|--------|
| **Agentic loop** | Runs until the LLM decides the incident is resolved |
| **Max turns guard** | Force-escalates and raises `MaxTurnsExceededError` after N turns — no infinite loops |
| **Real metrics** | Pass `localhost` as the server ID to get live CPU/memory via `psutil` |
| **Structured logging** | `logging` module throughout — set `--debug` for full tool payloads |
| **Tool registry** | Clean dispatch pattern — adding a new tool is one function + one schema entry |
| **CI** | GitHub Actions runs the full test suite on Python 3.10, 3.11, and 3.12 |

---

## Scenarios

| ID | Server | Issue | Expected Action |
|----|--------|-------|-----------------|
| A | `payment-server-01` | CPU at 98% | **Restart** |
| B | `db-node-02` | Healthy server | **No action** |
| C | `auth-service-03` | Memory at 95%, OOM errors | **Restart** |
| D | `search-index-09` | Dependency connection refused | **Escalate** |
| E | `frontend-node-04` | All 200 OKs | **No action** |

You can also pass `localhost` as the server ID to check your **real machine's** CPU and memory.

---

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/sagarpandya94/agent-it-responder.git
cd agent-it-responder
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your key
export OPENAI_API_KEY=sk-...
```

### 3. Run the agent

```bash
python main.py            # standard output
python main.py --debug    # full tool call payloads
```

### 4. Run the tests (no API key needed)

```bash
pytest tests/ -v
```

---

## Key Concepts Demonstrated

- **Agentic loops** — the model drives its own reasoning until it reaches a conclusion
- **Max turns / circuit breaker** — production agents must have hard limits to avoid runaway loops
- **Function calling** — tools defined as JSON schema, dispatched via a registry
- **Real system metrics** — `psutil` integration shows how mock data becomes real infrastructure
- **Structured logging** — `logging` module with configurable levels, not scattered `print()` calls
- **Separation of concerns** — agent logic, tools, data, and tests are fully decoupled
- **CI/CD** — GitHub Actions runs the suite on every push across multiple Python versions
