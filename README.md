# 🤖 Agent IT Responder

An autonomous IT incident response agent powered by OpenAI function-calling.
The agent investigates server health, reads logs, and takes action — restarting services or escalating to a human engineer — all without manual intervention.

---

## How It Works

The agent follows an **agentic loop**:

```
User reports an incident
        ↓
  Agent checks health + logs   ←──────────────────────┐
        ↓                                             │
  AI decides next action                             │
        ↓                                             │
  ┌─────────────┬──────────────────┐                 │
  │ CPU/Mem>90% │ Dependency error │  Neither?       │
  │             │                  │                  │
  ↓             ↓                  ↓                  │
Restart      Escalate        Report healthy ──────────┘
```

The LLM is given a system prompt with decision rules, a set of tools it can call, and the conversation history. It keeps calling tools until it has enough information to resolve or escalate the incident.

---

## Project Structure

```
agent-it-responder/
│
├── main.py                  # Entry point — runs all demo scenarios
│
├── agent/
│   ├── __init__.py
│   └── responder.py         # ITResponderAgent class (the agentic loop)
│
├── tools/
│   ├── __init__.py          # Tool registry + OpenAI function-calling schema
│   ├── health.py            # get_server_health()
│   ├── logs.py              # fetch_recent_logs()
│   ├── restart.py           # restart_service()
│   └── escalate.py          # escalate_to_engineer()
│
├── data/
│   └── scenarios.py         # Demo scenarios (used by main.py and tests)
│
├── tests/
│   ├── __init__.py
│   └── test_tools.py        # Unit tests for all tool functions (no API needed)
│
├── .env.example             # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Scenarios

| ID | Server | Issue | Expected Action |
|----|--------|-------|-----------------|
| A | `payment-server-01` | CPU at 98% | **Restart** |
| B | `db-node-02` | Healthy server | **No action** |
| C | `auth-service-03` | Memory at 95%, OOM errors | **Restart** |
| D | `search-index-09` | Dependency connection refused | **Escalate** |
| E | `frontend-node-04` | All 200 OKs | **No action** |

---

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/your-username/agent-it-responder.git
cd agent-it-responder
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
export OPENAI_API_KEY=sk-...
```

### 3. Run the agent

```bash
python main.py
```

### 4. Run the tests (no API key needed)

```bash
pytest tests/ -v
```

---

## Key Concepts Demonstrated

- **Agentic loops** — the model runs in a `while True` loop until it decides it's done
- **Function calling** — tools are defined as a JSON schema and dispatched via a registry
- **Tool separation** — each tool lives in its own module for easy extension
- **Separation of concerns** — agent logic, tool implementations, and data are fully decoupled
