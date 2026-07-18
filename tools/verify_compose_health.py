#!/usr/bin/env python3
"""Verify the nine-service Compose runtime and container security settings."""

from __future__ import annotations

import json
import subprocess
import urllib.request
from collections.abc import Sequence
from typing import cast

EXPECTED_SERVICES = {
    "api",
    "arbiter-rlp",
    "atlas",
    "docs-portal",
    "genesis",
    "operator-console",
    "postgres",
    "proof-portal",
    "swr",
}


def _run(arguments: Sequence[str]) -> str:
    result = subprocess.run(arguments, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _compose_records() -> tuple[dict[str, object], ...]:
    output = _run(("docker", "compose", "ps", "--format", "json"))
    if not output:
        return ()
    if output.lstrip().startswith("["):
        return tuple(cast(list[dict[str, object]], json.loads(output)))
    return tuple(cast(dict[str, object], json.loads(line)) for line in output.splitlines())


def _container_security(container_id: str) -> tuple[bool, str]:
    record = cast(list[dict[str, object]], json.loads(_run(("docker", "inspect", container_id))))[0]
    host = cast(dict[str, object], record["HostConfig"])
    readonly = host.get("ReadonlyRootfs") is True
    cap_drop = cast(list[str], host.get("CapDrop") or [])
    security_opt = cast(list[str], host.get("SecurityOpt") or [])
    passed = readonly and "ALL" in cap_drop and "no-new-privileges:true" in security_opt
    return passed, f"readonly={readonly},cap_drop={cap_drop},security_opt={security_opt}"


def _http_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:
        return cast(bytes, response.read()).decode("utf-8")


def main() -> int:
    records = _compose_records()
    by_service = {str(record["Service"]): record for record in records}
    failures: list[str] = []
    if set(by_service) != EXPECTED_SERVICES:
        failures.append(
            f"service set mismatch: expected={sorted(EXPECTED_SERVICES)} actual={sorted(by_service)}"
        )
    for service in sorted(EXPECTED_SERVICES & set(by_service)):
        record = by_service[service]
        state = str(record.get("State", ""))
        health = str(record.get("Health", ""))
        if state != "running" or health != "healthy":
            failures.append(f"{service}: state={state}, health={health}")
            continue
        secure, detail = _container_security(str(record["ID"]))
        if not secure:
            failures.append(f"{service}: insecure container settings: {detail}")
        print(f"{service}: healthy; {detail}")

    endpoint_expectations = {
        "http://127.0.0.1:8000/health/live": '"status":"live"',
        "http://127.0.0.1:4173/healthz": "live",
        "http://127.0.0.1:4174/healthz": "live",
        "http://127.0.0.1:4175/healthz": "live",
    }
    for url, expected in endpoint_expectations.items():
        body = _http_text(url)
        if expected not in body.replace(" ", ""):
            failures.append(f"{url}: expected {expected!r}, received {body!r}")
        print(f"{url}: {body.strip()}")

    genesis = json.loads(
        _run(("docker", "compose", "exec", "-T", "genesis", "genesis-emitter", "health"))
    )
    if genesis != {
        "status": "live",
        "service": "genesis",
        "version": "0.0.0.dev0",
        "authority": "evidence-only",
    }:
        failures.append(f"genesis evidence mismatch: {genesis!r}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    total = len(EXPECTED_SERVICES)
    print(f"compose runtime: {total}/{total} healthy and security settings verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
