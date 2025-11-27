"""Web Harvester agent (optional): placeholder for web scraping/hard fetching."""

from typing import Any, Dict


class WebHarvester:
    """Placeholder agent to record web harvest requests.

    This implementation intentionally does not perform network operations.
    It stores harvest requests for downstream processing.
    """

    def __init__(self) -> None:
        self.requests = []

    def request_harvest(self, url: str, depth: int = 0) -> Dict[str, Any]:
        req = {"url": url, "depth": int(depth), "status": "queued"}
        self.requests.append(req)
        return req
