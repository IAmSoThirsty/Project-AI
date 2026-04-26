"""
CLI interface adapter: Routes command-line operations through governance pipeline.

Old behavior: Direct imports and execution
New behavior: CLI → Router → Governance → Systems
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from app.core.runtime.router import route_request

logger = logging.getLogger(__name__)


def main() -> int:
    """
    CLI entrypoint that routes all operations through governance pipeline.
    
    Examples:
        python -m app.interfaces.cli --action ai.chat --prompt "Hello"
        python -m app.interfaces.cli --action persona.update --trait curiosity --value 0.8
    """
    parser = argparse.ArgumentParser(description="Project-AI CLI")
    parser.add_argument("--action", required=True, help="Action to perform")
    parser.add_argument("--prompt", help="Prompt for AI operations")
    parser.add_argument("--trait", help="Trait name for persona updates")
    parser.add_argument("--value", help="Value for updates")
    parser.add_argument("--model", help="AI model to use")
    parser.add_argument("--provider", help="AI provider (openai/huggingface)")
    parser.add_argument("--json-payload", help="Full payload as JSON string")

    args = parser.parse_args()

    # Build payload
    if args.json_payload:
        payload = json.loads(args.json_payload)
        payload["action"] = args.action
    else:
        payload = {
            "action": args.action,
        }
        
        if args.prompt:
            payload["prompt"] = args.prompt
            payload["task_type"] = "chat"
        if args.trait:
            payload["trait"] = args.trait
        if args.value:
            payload["value"] = args.value
        if args.model:
            payload["model"] = args.model
        if args.provider:
            payload["provider"] = args.provider

    # Route through governance pipeline
    try:
        response = route_request(source="cli", payload=payload)
        
        if response["status"] == "success":
            print(json.dumps(response["result"], indent=2))
            return 0
        else:
            print(f"Error: {response.get('error', 'Unknown error')}", file=sys.stderr)
            return 1
            
    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
