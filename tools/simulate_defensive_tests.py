"""Simulate defensive tests by generating synthetic modules that mimic malware patterns
and verifying them via the VerifierAgent pipeline.

This script is non-destructive: file writes are confined to a temp directory and no
actual external network calls are made. Each generated module is designed to
exercise a different suspicious behavior pattern.
"""
from __future__ import annotations

import argparse
import json
<<<<<<< HEAD
import os
=======
>>>>>>> 7680383fa2faae70c9879322f0f88b29211a4015
import random
import string
import sys
import tempfile
import time
from pathlib import Path
<<<<<<< HEAD
from typing import List
=======
>>>>>>> 7680383fa2faae70c9879322f0f88b29211a4015

# Ensure local package import
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from app.agents.border_patrol import VerifierAgent


def rand_name(prefix: str = "t") -> str:
    return prefix + "_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


PAYLOAD_TEMPLATES = [
    # CPU hog (infinite loop)
    ("cpu_hog", "while True:\n    pass\n"),
    # Sleep loop (long sleep)
    ("sleep_loop", "import time\nfor _ in range(10):\n    time.sleep(1)\n"),
    # Heavy allocation (may OOM)
    ("mem_hog", "a = 'x' * (10**8)\nprint(len(a))\n"),
    # File write attempt (confined to same dir)
    ("file_write", "with open('dropped.txt','w') as f:\n    f.write('malicious payload')\n"),
    # Exec of decoded string (obfuscated)
    ("obfuscated_exec", "import base64\ncode = base64.b64decode('%s')\nexec(code)\n"),
    # Nested import and eval
    ("nested_eval", "data = '2+2'\nprint(eval(data))\n"),
    # Syntax error
    ("syntax_error", "def broken(:\n    pass\n"),
    # Exception raising
    ("raise_exception", "raise RuntimeError('simulated crash')\n"),
    # Attempt to spawn subprocess (will be limited)
    ("subprocess_spawn", "import subprocess\nsubprocess.Popen(['echo','hello'])\n"),
    # Attempt network socket to localhost (allowed but harmless)
    ("socket_probe", "import socket\ns=socket.socket(); s.settimeout(0.1)\ntry:\n    s.connect(('127.0.0.1', 1))\nexcept Exception as e:\n    pass\nfinally:\n    s.close()\n"),
]


def build_obfuscated_inner():
    inner = "print('hello from obfuscated')"
    import base64

    return base64.b64encode(inner.encode()).decode()


<<<<<<< HEAD
def generate_payloads(count: int, out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files: List[Path] = []
    for i in range(count):
=======
def generate_payloads(count: int, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for _i in range(count):
>>>>>>> 7680383fa2faae70c9879322f0f88b29211a4015
        name = rand_name('sim') + '.py'
        path = out_dir / name
        choice = random.choice(PAYLOAD_TEMPLATES)
        payload_type = choice[0]
        template = choice[1]
        if payload_type == 'obfuscated_exec':
            payload = template % build_obfuscated_inner()
        elif payload_type == 'mem_hog':
            # scale memory attempts to be safer on CI
            payload = "a = 'x' * (10**7)\nprint(len(a))\n"
        else:
            payload = template
        # Add small wrapper to reduce accidental hazards
<<<<<<< HEAD
        wrapper = "# simulated payload type=%s\n" % payload_type
=======
        wrapper = f"# simulated payload type={payload_type}\n"
>>>>>>> 7680383fa2faae70c9879322f0f88b29211a4015
        wrapper += payload
        path.write_text(wrapper)
        files.append(path)
    return files


def run_simulation(count: int, data_dir: Path, concurrency: int = 4, timeout: int = 8, bypass_ratio: float = 0.0):
    out = {
        "count": count,
        "timestamp": time.time(),
        "results": [],
        "summary": {},
        "bypass_ratio": bypass_ratio,
    }
    tmp = Path(tempfile.mkdtemp(prefix="sim_def_"))
    payloads = generate_payloads(count, tmp)

    verifier = VerifierAgent(agent_id="sim-runner", data_dir=str(data_dir), max_workers=concurrency, timeout=timeout)

    detected = 0
    bypassed = 0
    for p in payloads:
        start = time.time()
        simulated_bypass = False
        if bypass_ratio > 0 and random.random() < bypass_ratio:
            # simulate that this payload was introduced/ignored by gatekeepers and thus bypasses verification
            simulated_bypass = True
            verdict = 'clean'
            report = {"success": True, "verdict": 'clean', "sandbox": {}, "simulated_bypass": True}
            bypassed += 1
            took = 0.0
        else:
            report = verifier.verify(str(p))
            verdict = report.get('verdict') if isinstance(report, dict) else None
            took = time.time() - start
        if verdict != 'clean':
            detected += 1
        out['results'].append({
            'file': str(p.name),
            'verdict': verdict,
            'time': took,
            'report': report,
            'simulated_bypass': simulated_bypass,
        })

    out['summary'] = {
        'detected': detected,
        'clean': count - detected,
        'bypassed': bypassed,
        'duration': time.time() - out['timestamp'],
    }

    # persist
    data_dir = Path(data_dir)
    dest = data_dir / 'monitoring'
    dest.mkdir(parents=True, exist_ok=True)
    out_file = dest / f'simulation_results_{int(time.time())}.json'
    out_file.write_text(json.dumps(out, indent=2))
    print(f"Simulation complete: {out['summary']}")
    print(f"Results saved to {out_file}")
    return out


def main():
    parser = argparse.ArgumentParser(description='Run defensive simulation payloads through verifier')
    parser.add_argument('--count', type=int, default=250)
    parser.add_argument('--data-dir', type=str, default='data')
    parser.add_argument('--concurrency', type=int, default=4)
    parser.add_argument('--timeout', type=int, default=8)
    parser.add_argument('--bypass-ratio', type=float, default=0.0, help='Fraction of payloads that simulate bypass (0.0-1.0)')
    args = parser.parse_args()

<<<<<<< HEAD
    res = run_simulation(args.count, Path(args.data_dir), concurrency=args.concurrency, timeout=args.timeout, bypass_ratio=args.bypass_ratio)
=======
    run_simulation(args.count, Path(args.data_dir), concurrency=args.concurrency, timeout=args.timeout, bypass_ratio=args.bypass_ratio)
>>>>>>> 7680383fa2faae70c9879322f0f88b29211a4015
    print('Done')


if __name__ == '__main__':
    main()
