"""CLI to manage the Oversight policy file for AIPersona.

Usage:
  python tools/manage_oversight_policy.py view   # prints current policy
  python tools/manage_oversight_policy.py validate  # validates existing policy
  python tools/manage_oversight_policy.py set <file>  # set policy from given JSON file (validated)
  python tools/manage_oversight_policy.py init  # write a default policy to persona dir

By default the persona dir is 'data/ai_persona'. Use --persona-dir to change.
"""
import argparse
import json
import os
import sys
from typing import Optional

try:
    from app.agents.oversight import OversightAgent
except Exception:
    # If running outside package context, try relative import
    try:
        from ..app.agents.oversight import OversightAgent  # type: ignore
    except Exception:
        OversightAgent = None  # type: ignore


DEFAULT_POLICY = {
    "allow": ["please proceed"],
    "deny": ["destroy the world", "genocide"],
    "allow_regex": [],
    "deny_regex": [],
    "keyword_severity": {"kill": 1.0, "harm": 0.9},
    "threshold": 0.6,
    "scoring": "max",
}


def persona_policy_path(persona_dir: str) -> str:
    os.makedirs(persona_dir, exist_ok=True)
    return os.path.join(persona_dir, 'oversight_policy.json')


def cmd_view(persona_dir: str) -> int:
    path = persona_policy_path(persona_dir)
    if not os.path.exists(path):
        print(f"No policy found at {path}")
        return 1
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(json.dumps(data, indent=2))
    return 0


def cmd_validate(persona_dir: str) -> int:
    path = persona_policy_path(persona_dir)
    if not os.path.exists(path):
        print(f"No policy found at {path}")
        return 2
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if OversightAgent is None:
        print("OversightAgent not importable; cannot validate policy programmatically.")
        return 3
    agent = OversightAgent()
    valid, errors = agent.validate_policy_schema(data)
    if valid:
        print("Policy is valid")
        return 0
    print("Policy invalid:")
    for e in errors:
        print(' -', e)
    return 4


def cmd_set(persona_dir: str, infile: str) -> int:
    if not os.path.exists(infile):
        print(f"Input file not found: {infile}")
        return 2
    with open(infile, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Failed to parse JSON: {e}")
            return 3
    if OversightAgent is None:
        print("OversightAgent not importable; cannot validate policy programmatically.")
        return 4
    agent = OversightAgent()
    valid, errors = agent.validate_policy_schema(data)
    if not valid:
        print("Policy invalid; refusing to set:")
        for e in errors:
            print(' -', e)
        return 5
    # save to persona dir
    path = persona_policy_path(persona_dir)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to write policy: {e}")
        return 6
    print(f"Policy written to {path}")
    return 0


def cmd_init(persona_dir: str) -> int:
    path = persona_policy_path(persona_dir)
    if os.path.exists(path):
        print(f"Policy already exists at {path}")
        return 1
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_POLICY, f, indent=2)
    except Exception as e:
        print(f"Failed to write default policy: {e}")
        return 2
    print(f"Default policy written to {path}")
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description='Manage Oversight policy in persona dir')
    parser.add_argument('command', choices=['view', 'validate', 'set', 'init'])
    parser.add_argument('file', nargs='?', help='Input file for set')
    parser.add_argument('--persona-dir', '-p', default=os.path.join('data', 'ai_persona'))
    args = parser.parse_args(argv)

    if args.command == 'view':
        return cmd_view(args.persona_dir)
    if args.command == 'validate':
        return cmd_validate(args.persona_dir)
    if args.command == 'set':
        if not args.file:
            print('set requires a file argument')
            return 2
        return cmd_set(args.persona_dir, args.file)
    if args.command == 'init':
        return cmd_init(args.persona_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
