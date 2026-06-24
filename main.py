"""
Entry point for the IT Incident Responder agent.

Usage:
    python main.py

Requires:
    OPENAI_API_KEY set as an environment variable.
"""

import os
from openai import OpenAI

from agent import ITResponderAgent
from data.scenarios import SCENARIOS


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Export it before running:  export OPENAI_API_KEY=sk-..."
        )

    client = OpenAI(api_key=api_key)
    agent  = ITResponderAgent(client=client, model="gpt-4o")

    for scenario in SCENARIOS:
        print(f"\n{'#'*60}")
        print(f"  SCENARIO {scenario['id']}: {scenario['description']}")
        print(f"{'#'*60}")
        agent.run(scenario["user_issue"])


if __name__ == "__main__":
    main()
