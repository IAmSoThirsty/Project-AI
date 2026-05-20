"""
Normalization utilities for Cerberus SASE core, including Tor exit node detection.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request

_TOR_EXIT_LIST_URL = "https://check.torproject.org/exit-addresses"
_EXIT_ADDR_RE = re.compile(r"^ExitAddress\s+(\S+)", re.MULTILINE)
_FALLBACK_IPS: frozenset[str] = frozenset({"185.220.101.1", "185.220.101.2"})


class TorDetector:
    def __init__(self) -> None:
        self.tor_exit_nodes: set[str] = self._fetch_exit_nodes()

    def _fetch_exit_nodes(self) -> set[str]:
        try:
            with urllib.request.urlopen(_TOR_EXIT_LIST_URL) as resp:
                data = resp.read().decode("utf-8", errors="replace")
            ips = set(_EXIT_ADDR_RE.findall(data))
            return ips if ips else set(_FALLBACK_IPS)
        except (urllib.error.URLError, TimeoutError, OSError):
            return set(_FALLBACK_IPS)

    def is_tor_exit(self, ip: str) -> bool:
        return ip in self.tor_exit_nodes
