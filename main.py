"""
Entry point for the IT Incident Responder agent.

Usage:
    python main.py              # INFO level output
    python main.py --debug      # DEBUG level (shows full tool payloads)

Requires:
    OPENAI_API_KEY set as an environment variable.
"""

import os
import sys
import logging
from openai import OpenAI

from agent import ITResponderAgent, MaxTurnsExceededError, setup_logging
from data.scenarios import SCENARIOS

logger = logging.getLogger(__name__)


def main():
    log_level = "DEBUG" if "--debug" in sys.argv else "INFO"
    setup_logging(level=log_level)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.critical(
            "OPENAI_API_KEY environment variable is not set. "
            "Export it before running:  export OPENAI_API_KEY=sk-..."
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    agent  = ITResponderAgent(client=client, model="gpt-4o", max_turns=10)

    for scenario in SCENARIOS:
        logger.info("=" * 60)
        logger.info("SCENARIO %s: %s", scenario["id"], scenario["description"])
        logger.info("=" * 60)

        try:
            agent.run(scenario["user_issue"])
        except MaxTurnsExceededError as e:
            logger.error("Scenario %s failed: %s", scenario["id"], e)


if __name__ == "__main__":
    main()
