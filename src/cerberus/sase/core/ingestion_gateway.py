"""
SASE - Sovereign Adversarial Signal Engine
L2: Telemetry Ingestion Gateway

Handles telemetry event ingestion with Avro serialization, immutable storage, and audit hashing.

INGESTION FLOW:
1. TLS termination
2. Input sanitization
3. ASN lookup
4. GeoIP enrichment
5. Token correlation
6. Event hashing
7. Append-only queue
8. Immutable event store
"""

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger("SASE.L2.Ingestion")


class ArtifactType(Enum):
    """Types of adversarial artifacts"""

    DNS_RESOLUTION = "DNS_RESOLUTION"
    HTTP_CALLBACK = "HTTP_CALLBACK"
    CREDENTIAL_MISUSE = "CREDENTIAL_MISUSE"
    OAUTH_VALIDATION = "OAUTH_VALIDATION"
    API_MISUSE = "API_MISUSE"
    WEBHOOK_INVOCATION = "WEBHOOK_INVOCATION"
    SYNTHETIC_LEAK = "SYNTHETIC_LEAK"


class TransportType(Enum):
    """Network transport protocols"""

    HTTP = "HTTP"
    HTTPS = "HTTPS"
    DNS = "DNS"
    TCP = "TCP"
    UDP = "UDP"
    OTHER = "OTHER"


@dataclass
class GeoLocation:
    """Geographic location data"""

    country: str  # ISO 3166-1 alpha-2
    city: str | None = None
    lat: float | None = None
    lon: float | None = None
    region: str | None = None


@dataclass
class AdversarialEvent:
    """
    Canonical adversarial event

    Matches event.avsc Avro schema
    """

    event_id: str
    ingest_timestamp: int  # Unix ms
    source_ip: str
    asn: str
    geo: GeoLocation
    artifact_id: str
    artifact_type: ArtifactType
    campaign_id: str
    transport_type: TransportType
    raw_payload_hash: str
    model_version: str
    signature: str
    user_agent: str | None = None
    enrichment: dict[str, Any] | None = None  # Added by L3

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (for Avro/JSON)"""
        return {
            "event_id": self.event_id,
            "ingest_timestamp": self.ingest_timestamp,
            "source_ip": self.source_ip,
            "asn": self.asn,
            "geo": {
                "country": self.geo.country,
                "city": self.geo.city,
                "lat": self.geo.lat,
                "lon": self.geo.lon,
                "region": self.geo.region,
            },
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type.value,
            "campaign_id": self.campaign_id,
            "user_agent": self.user_agent,
            "transport_type": self.transport_type.value,
            "raw_payload_hash": self.raw_payload_hash,
            "model_version": self.model_version,
            "signature": self.signature,
            "enrichment": self.enrichment,
        }


class EventSerializer:
    """
    Avro event serialization

    Serializes events according to event.avsc schema
    """

    def __init__(self, schema_path: str = None):
        self.schema_path = schema_path
        # TODO: Load Avro schema from file for full validation

    def serialize(self, event: AdversarialEvent) -> bytes:
        """Serialize event to Avro binary format"""
        # For now, use JSON (TODO: implement proper Avro)
        event_dict = event.to_dict()
        json_str = json.dumps(event_dict, sort_keys=True)
        return json_str.encode("utf-8")

    def deserialize(self, data: bytes) -> AdversarialEvent:
        """Deserialize Avro binary to event"""
        # For now, use JSON (TODO: implement proper Avro)
        json_str = data.decode("utf-8")
        event_dict = json.loads(json_str)

        return AdversarialEvent(
            event_id=event_dict["event_id"],
            ingest_timestamp=event_dict["ingest_timestamp"],
            source_ip=event_dict["source_ip"],
            asn=event_dict["asn"],
            geo=GeoLocation(**event_dict["geo"]),
            artifact_id=event_dict["artifact_id"],
            artifact_type=ArtifactType(event_dict["artifact_type"]),
            campaign_id=event_dict["campaign_id"],
            transport_type=TransportType(event_dict["transport_type"]),
            raw_payload_hash=event_dict["raw_payload_hash"],
            model_version=event_dict["model_version"],
            signature=event_dict["signature"],
            user_agent=event_dict.get("user_agent"),
            enrichment=event_dict.get("enrichment"),
        )


class ImmutableEventStore:
    """
    Append-only immutable event storage

    Events cannot be modified once written
    All events are cryptographically hashed
    """

    def __init__(self, storage_path: str = "sase_events.log"):
        self.storage_path = storage_path
        self.event_count = 0
        self.event_hashes: list[str] = []

    def store(self, event: AdversarialEvent) -> str:
        """
        Store event immutably

        Returns event hash for Merkle tree
        """
        # Serialize event
        serializer = EventSerializer()
        event_bytes = serializer.serialize(event)

        # Hash event
        event_hash = hashlib.sha256(event_bytes).hexdigest()

        # Append to store (immutable)
        with open(self.storage_path, "ab") as f:
            f.write(event_bytes + b"\n")

        self.event_count += 1
        self.event_hashes.append(event_hash)

        logger.info(f"Event stored: {event.event_id} hash={event_hash[:16]}")

        return event_hash

    def get_event_hashes(self, start: int = 0, end: int = None) -> list[str]:
        """Get event hashes for Merkle tree construction"""
        if end is None:
            end = len(self.event_hashes)
        return self.event_hashes[start:end]


class TelemetryGateway:
    """
    L2: Telemetry Ingestion Gateway

    Processes raw telemetry through ingestion pipeline
    """

    def __init__(self, model_version: str = "1.0.0"):
        self.model_version = model_version
        self.serializer = EventSerializer()
        self.store = ImmutableEventStore()
        self.pending_queue: list[AdversarialEvent] = []

    def ingest(self, raw_telemetry: dict[str, Any]) -> AdversarialEvent:
        """
        Ingest raw telemetry event

        INGESTION FLOW:
        1. TLS termination (assumed handled by edge)
        2. Input sanitization
        3. ASN lookup
        4. GeoIP enrichment
        5. Token correlation
        6. Event hashing
        7. Append-only queue
        8. Immutable storage
        """

        # 1. TLS termination - handled by edge

        # 2. Input sanitization
        sanitized = self._sanitize_input(raw_telemetry)

        # 3. ASN lookup
        asn = self._lookup_asn(sanitized["source_ip"])

        # 4. GeoIP enrichment
        geo = self._enrich_geoip(sanitized["source_ip"])

        # 5. Token correlation
        campaign_id = self._correlate_token(sanitized.get("artifact_id", "UNKNOWN"))

        # 6. Event hashing
        raw_payload = json.dumps(sanitized, sort_keys=True)
        payload_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

        # Create event
        event = AdversarialEvent(
            event_id=str(uuid.uuid4()),
            ingest_timestamp=int(time.time() * 1000),
            source_ip=sanitized["source_ip"],
            asn=asn,
            geo=geo,
            artifact_id=sanitized.get("artifact_id", "UNKNOWN"),
            artifact_type=ArtifactType(sanitized.get("artifact_type", "HTTP_CALLBACK")),
            campaign_id=campaign_id,
            transport_type=TransportType(sanitized.get("transport", "HTTP")),
            raw_payload_hash=payload_hash,
            model_version=self.model_version,
            signature="",  # Will be signed by HSM (L9/L12)
            user_agent=sanitized.get("user_agent"),
        )

        # 7. Append to queue
        self.pending_queue.append(event)

        # 8. Store immutably
        event_hash = self.store.store(event)

        logger.info(f"Telemetry ingested: {event.event_id}")

        return event

    def _sanitize_input(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Sanitize and validate input"""
        # Basic sanitization
        return {
            "source_ip": raw.get("ip", raw.get("source_ip", "0.0.0.0")),
            "artifact_id": str(raw.get("artifact_id", "UNKNOWN")),
            "artifact_type": raw.get("type", "HTTP_CALLBACK"),
            "transport": raw.get("transport", "HTTP"),
            "user_agent": raw.get("user_agent", raw.get("ua")),
        }

    def _lookup_asn(self, ip: str) -> str:
        """Look up ASN for IP address"""
        # TODO: Implement real ASN lookup
        return "AS13335"  # Cloudflare example

    def _enrich_geoip(self, ip: str) -> GeoLocation:
        """Enrich with GeoIP data"""
        # TODO: Implement real GeoIP lookup
        return GeoLocation(country="US", city="San Francisco", lat=37.7749, lon=-122.4194, region="CA")

    def _correlate_token(self, artifact_id: str) -> str:
        """Correlate artifact to campaign"""
        # TODO: Implement campaign correlation
        return f"campaign-{artifact_id[:8]}"

    def flush_queue(self) -> int:
        """Flush pending queue (for batch processing)"""
        count = len(self.pending_queue)
        self.pending_queue = []
        return count


__all__ = [
    "ArtifactType",
    "TransportType",
    "GeoLocation",
    "AdversarialEvent",
    "EventSerializer",
    "ImmutableEventStore",
    "TelemetryGateway",
]
