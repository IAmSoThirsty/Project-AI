"""Runtime helper to manage oversight policy via AIPersona instance.

This script is intended to be used on the machine where an AIPersona runs
and will load/save the policy via the persona's API (local file operations).

Usage examples:
  python tools/manage_oversight_policy_runtime.py --data-dir data view
  python tools/manage_oversight_policy_runtime.py --data-dir data set path/to/new_policy.json --actor admin
  python tools/manage_oversight_policy_runtime.py --data-dir data init --actor bootstrap
"""
import argparse
import json
import os
import sys

try:
    from app.core.ai_persona import AIPersona
except Exception:
    try:
        from ..src.app.core.ai_persona import AIPersona
    except Exception:
        AIPersona = None


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description='Manage oversight policy (runtime)')
    parser.add_argument('--data-dir', default='data', help='Root data directory where persona lives')
    parser.add_argument('--actor', default=None, help='Actor name to include in audit events')
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('view')
    setp = sub.add_parser('set')
    setp.add_argument('file', help='Path to policy JSON to set')
    sub.add_parser('init')

    args = parser.parse_args(argv)
    if AIPersona is None:
        print('AIPersona import failed; run from project root or ensure package is on PYTHONPATH')
        return 2

    persona = AIPersona(data_dir=args.data_dir)

    policy_path = os.path.join(persona.persona_dir, 'oversight_policy.json')

    if args.cmd == 'view':
        if os.path.exists(policy_path):
            with open(policy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(json.dumps(data, indent=2))
            return 0
        else:
            print('No policy found at', policy_path)
            return 1

    if args.cmd == 'set':
        src = args.file
        if not os.path.exists(src):
            print('Policy file not found:', src)
            return 2
        # Ask oversight agent to load and then save via persona for audit
        try:
            persona.oversight_agent.load_policy_from_file(src)
            persona.save_oversight_policy(actor=args.actor)
            print('Policy updated and saved to', policy_path)
            return 0
        except Exception as e:
            print('Failed to set policy:', e)
            return 3

    if args.cmd == 'init':
        # Persona init already creates default on construction; save explicit audit with actor if provided
        try:
            persona.save_oversight_policy(actor=args.actor)
            print('Policy initialized at', policy_path)
            return 0
        except Exception as e:
            print('Failed to init policy:', e)
            return 3

    parser.print_help()
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
