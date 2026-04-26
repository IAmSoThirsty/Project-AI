from __future__ import annotations

import atexit
import hashlib
import hmac
import json
import os
import socket
import struct
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urlparse
from uuid import uuid4

from waterfall.v1 import waterfall_pb2

try:
    from app.infrastructure.vpn.backends import VPNBackendFactory
except Exception:  # pragma: no cover - optional runtime dependency
    VPNBackendFactory = None

try:
    from app.infrastructure.vpn.vpn_manager import VPNManager
except Exception:  # pragma: no cover - optional runtime dependency
    VPNManager = None

SERVICE_VERSION = "0.1.0"
PROTOCOL_VERSION = "waterfall.v1"
WATERFALL_UPDATE_SIGNATURE_VERSION = "waterfall-update-v1"
WATERFALL_UPDATE_METADATA_PREFIX = "wfmeta:"
SUPPORTED_CAPABILITIES = (
    "health",
    "search",
    "consigliere",
    "security",
    "download-gate",
    "ledger",
    "updates",
)
DEFAULT_PROVIDERS = ("duckduckgo", "startpage", "kagi")
FALLBACK_SEARCH_PROVIDER_URLS = {
    "duckduckgo": "https://duckduckgo.com/?q=",
    "startpage": "https://www.startpage.com/sp/search?query=",
    "kagi": "https://kagi.com/search?q=",
}
SUSPICIOUS_DOWNLOAD_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".dll",
    ".exe",
    ".hta",
    ".jar",
    ".js",
    ".msi",
    ".ps1",
    ".scr",
    ".vbs",
}


@dataclass(frozen=True)
class TcpLoopbackEndpoint:
    host: str
    port: int


@dataclass(frozen=True)
class UnixSocketEndpoint:
    path: str


@dataclass
class OrchestratorState:
    vpn_enabled: bool = False
    vpn_server: str = ""
    privacy_events: list[waterfall_pb2.PrivacyEvent] = field(default_factory=list)
    vpn_manager: Any | None = None
    available_vpn_backends: list[str] = field(default_factory=list)
    security_toolkit_root: str = ""
    toolkit_inventory_online: bool = False

    @property
    def ledger_head(self) -> str:
        if not self.privacy_events:
            return ""
        latest = self.privacy_events[-1]
        return f"{latest.type}:{latest.timestamp}"


def _parse_endpoint(endpoint_spec: str) -> TcpLoopbackEndpoint | UnixSocketEndpoint:
    if endpoint_spec.startswith("tcp://"):
        parsed = urlparse(endpoint_spec)
        host = parsed.hostname or ""
        port = parsed.port or 0
        if host not in {"127.0.0.1", "localhost"}:
            raise RuntimeError("WaterFall orchestrator only accepts loopback TCP endpoints.")
        if port <= 0 or port > 65535:
            raise RuntimeError("WaterFall orchestrator received an invalid TCP port.")
        return TcpLoopbackEndpoint(host=host, port=port)

    if os.name == "nt":
        raise RuntimeError(
            "WaterFall orchestrator bootstrap supports loopback TCP on Windows. "
            "Set WATERFALL_ORCHESTRATOR_ENDPOINT=tcp://127.0.0.1:<port>."
        )

    return UnixSocketEndpoint(path=endpoint_spec)


def _recv_exact(connection: socket.socket, length: int) -> bytes | None:
    payload = bytearray()
    while len(payload) < length:
        chunk = connection.recv(length - len(payload))
        if not chunk:
            if not payload:
                return None
            raise ConnectionError("WaterFall orchestrator connection closed mid-frame.")
        payload.extend(chunk)
    return bytes(payload)


def _read_frame(connection: socket.socket) -> bytes | None:
    header = _recv_exact(connection, 4)
    if header is None:
        return None
    frame_length = struct.unpack(">I", header)[0]
    if frame_length <= 0:
        raise ConnectionError("WaterFall orchestrator received an invalid frame length.")
    return _recv_exact(connection, frame_length)


def _write_frame(connection: socket.socket, payload: bytes) -> None:
    connection.sendall(struct.pack(">I", len(payload)) + payload)


def _build_handshake_response(
    request: waterfall_pb2.BridgeHandshakeRequest,
) -> waterfall_pb2.BridgeHandshakeResponse:
    granted = [capability for capability in request.requested_capabilities if capability in SUPPORTED_CAPABILITIES]
    response = waterfall_pb2.BridgeHandshakeResponse(
        accepted=request.protocol_version == PROTOCOL_VERSION,
        protocol_version=PROTOCOL_VERSION,
        service_version=SERVICE_VERSION,
        granted_capabilities=granted,
        message="WaterFall Python orchestrator is online."
        if request.protocol_version == PROTOCOL_VERSION
        else "Protocol mismatch.",
    )
    return response


def _build_search_response(query: waterfall_pb2.SearchQuery) -> waterfall_pb2.SearchResponse:
    providers = list(query.providers) or list(DEFAULT_PROVIDERS)
    response = waterfall_pb2.SearchResponse(
        total_hits=0,
        query_id=f"query-{uuid4().hex}",
    )

    for provider in providers:
        provider_url = FALLBACK_SEARCH_PROVIDER_URLS.get(provider)
        if not provider_url:
            response.warnings.append(f"provider:{provider}:unsupported")
            continue

        response.results.add(
            id=f"{provider}-{uuid4().hex}",
            title=f'{provider.title()} results for "{query.query}"',
            url=f"{provider_url}{quote_plus(query.query)}",
            snippet="WaterFall orchestrator is currently providing transparent provider launch targets.",
            provider=provider,
            published="",
            relevance_score=0.15,
            categories=["meta-aggregation", provider],
        )

    response.total_hits = len(response.results)
    if not response.results:
        response.warnings.append("no-provider-results")
    return response


def _build_audit_response(
    request: waterfall_pb2.ConsigliereAuditRequest,
) -> waterfall_pb2.ConsigliereAuditResponse:
    providers = {result.provider for result in request.raw_results if result.provider}
    categories = sorted({category for result in request.raw_results for category in result.categories})
    response = waterfall_pb2.ConsigliereAuditResponse()
    response.privacy_flags.append("consigliere-bootstrap-active")
    if len(providers) <= 1:
        response.privacy_flags.append("single-provider-lane")
    if categories:
        response.source_clusters.extend(categories)
    else:
        response.source_clusters.append("unclustered")
    response.explanation_cards.extend(
        [
            "WaterFall Consigliere is currently operating in audited bootstrap mode.",
            f"Query lanes observed: {len(providers) or 1}.",
            f"Results observed: {len(request.raw_results)}.",
        ]
    )
    for provider in providers:
        response.optional_summaries[provider] = (
            "WaterFall is preserving raw provider ordering while the sovereign ranking lane comes online."
        )
    return response


def _build_security_status(state: OrchestratorState) -> waterfall_pb2.SecurityStatus:
    if state.vpn_manager is not None:
        try:
            vpn_status = state.vpn_manager.get_status()
            state.vpn_enabled = bool(
                vpn_status.get("connected") or vpn_status.get("active")
            )
            route = vpn_status.get("route") or []
            if route:
                state.vpn_server = route[-1].get("endpoint", state.vpn_server)
        except Exception:
            pass

    warnings = [
        "WaterFall orchestrator bootstrap is active; deeper subsystem bindings are still coming online."
    ]
    if state.available_vpn_backends:
        warnings.append(
            "vpn-backends:" + ",".join(sorted(state.available_vpn_backends))
        )
    else:
        warnings.append("vpn-backends:none-detected")
    warnings.append(
        "security-architect-toolkit:"
        + ("online" if state.toolkit_inventory_online else "offline")
    )

    return waterfall_pb2.SecurityStatus(
        vpn_enabled=state.vpn_enabled,
        firewall_profiles=[
            "browser-partition-kill-switch",
            "tracker-blocking",
            "download-gate-bootstrap",
            "permissions-lockdown",
        ],
        microvm_health="unknown",
        ledger_head=state.ledger_head,
        download_gate_online=True,
        orchestrator_mode="online",
        warnings=warnings,
    )


def _discover_available_vpn_backends() -> list[str]:
    if VPNBackendFactory is None:
        return []

    available_backends: list[str] = []
    for protocol in ("wireguard", "openvpn", "ikev2"):
        try:
            backend = VPNBackendFactory.create_backend(protocol, {})
            if backend and backend.check_availability():
                available_backends.append(protocol)
        except Exception:
            continue

    return available_backends


def _build_initial_state() -> OrchestratorState:
    state = OrchestratorState()
    state.available_vpn_backends = _discover_available_vpn_backends()
    toolkit_root = Path(__file__).resolve().parents[3] / "trunk" / "super" / "penetration-testing-tools"
    state.security_toolkit_root = str(toolkit_root)
    state.toolkit_inventory_online = toolkit_root.exists()

    if VPNManager is not None:
        try:
            state.vpn_manager = VPNManager(
                {
                    "enabled": True,
                    "multi_hop": True,
                    "hop_count": 3,
                    "stealth_mode": True,
                    "kill_switch": True,
                    "dns_leak_protection": True,
                    "ipv6_leak_protection": True,
                    "protocol_fallback": state.available_vpn_backends
                    or ["wireguard", "openvpn", "ikev2"],
                }
            )
        except Exception:
            state.vpn_manager = None

    return state


def _scan_download(request: waterfall_pb2.DownloadScanRequest) -> waterfall_pb2.DownloadScanVerdict:
    extension = Path(request.path).suffix.lower()
    exists = Path(request.path).exists() if request.path else False
    risky = extension in SUSPICIOUS_DOWNLOAD_EXTENSIONS
    findings = []

    if not exists:
        findings.append("target-missing")
    if risky:
        findings.append(f"suspicious-extension:{extension}")

    verdict = "review" if risky or not exists else "clean"
    risk_score = 72 if risky else (35 if not exists else 14)
    recommended_action = "quarantine" if risky else ("review" if not exists else "allow")

    return waterfall_pb2.DownloadScanVerdict(
        verdict=verdict,
        risk_score=risk_score,
        findings=findings,
        recommended_action=recommended_action,
    )


def _empty_response() -> waterfall_pb2.Empty:
    return waterfall_pb2.Empty()


def _build_update_signature_payload(
    version: str,
    url: str,
    channel: str,
    available: bool,
    visible_notes: list[str],
    artifact_sha256: str,
    artifact_name: str,
    released_at: str,
) -> str:
    return "\n".join(
        [
            WATERFALL_UPDATE_SIGNATURE_VERSION,
            f"version={version}",
            f"url={url}",
            f"channel={channel}",
            f"available={1 if available else 0}",
            f"artifact_sha256={artifact_sha256}",
            f"artifact_name={artifact_name}",
            f"released_at={released_at}",
            f"notes={json.dumps(visible_notes, ensure_ascii=True, separators=(',', ':'))}",
        ]
    )


def _build_update_manifest() -> waterfall_pb2.UpdateManifest:
    update_version = os.environ.get("WATERFALL_UPDATE_AVAILABLE_VERSION", "").strip() or SERVICE_VERSION
    update_url = os.environ.get("WATERFALL_UPDATE_URL", "").strip()
    update_channel = os.environ.get("WATERFALL_UPDATE_CHANNEL", "").strip() or "stable"
    update_artifact_sha256 = os.environ.get("WATERFALL_UPDATE_ARTIFACT_SHA256", "").strip().lower()
    update_artifact_name = os.environ.get("WATERFALL_UPDATE_ARTIFACT_NAME", "").strip()
    update_released_at = os.environ.get("WATERFALL_UPDATE_RELEASED_AT", "").strip()
    update_notes = [
        entry.strip()
        for entry in os.environ.get("WATERFALL_UPDATE_NOTES", "").split("||")
        if entry.strip()
    ]
    update_signing_key = os.environ.get("WATERFALL_UPDATE_SIGNING_KEY", "").strip()
    update_available = os.environ.get("WATERFALL_UPDATE_AVAILABLE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if not update_url:
        update_available = False

    if not update_artifact_name and update_url:
        try:
            update_artifact_name = Path(urlparse(update_url).path).name
        except Exception:
            update_artifact_name = ""

    visible_notes = update_notes or [
        "WaterFall updater bootstrap is online, but no signed release manifest was configured."
    ]
    metadata_notes = []

    if update_artifact_sha256:
        metadata_notes.append(
            f"{WATERFALL_UPDATE_METADATA_PREFIX}artifact_sha256={update_artifact_sha256}"
        )
    if update_artifact_name:
        metadata_notes.append(f"{WATERFALL_UPDATE_METADATA_PREFIX}artifact_name={update_artifact_name}")
    if update_released_at:
        metadata_notes.append(f"{WATERFALL_UPDATE_METADATA_PREFIX}released_at={update_released_at}")

    signature = ""
    if update_available and update_signing_key and update_artifact_sha256 and update_url:
        signature = hmac.new(
            update_signing_key.encode("utf-8"),
            _build_update_signature_payload(
                update_version,
                update_url,
                update_channel,
                update_available,
                visible_notes,
                update_artifact_sha256,
                update_artifact_name,
                update_released_at,
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    return waterfall_pb2.UpdateManifest(
        version=update_version,
        signature=signature,
        url=update_url,
        channel=update_channel,
        available=update_available,
        notes=[*visible_notes, *metadata_notes],
        integrity_state="unknown",
    )


def _handle_method(
    method: str,
    payload: bytes,
    state: OrchestratorState,
) -> tuple[bytes, Iterable[str]]:
    if method == "Ping":
        response = waterfall_pb2.PingResponse(
            ok=True,
            version=SERVICE_VERSION,
            protocol_version=PROTOCOL_VERSION,
            capabilities=SUPPORTED_CAPABILITIES,
        )
        return response.SerializeToString(), ()

    if method == "Query":
        request = waterfall_pb2.SearchQuery()
        request.ParseFromString(payload)
        return _build_search_response(request).SerializeToString(), ()

    if method == "AuditWithConsigliere":
        request = waterfall_pb2.ConsigliereAuditRequest()
        request.ParseFromString(payload)
        return _build_audit_response(request).SerializeToString(), ()

    if method == "GetSecurityStatus":
        return _build_security_status(state).SerializeToString(), ()

    if method == "SetVPNState":
        request = waterfall_pb2.VPNStateRequest()
        request.ParseFromString(payload)
        state.vpn_server = request.server
        if state.vpn_manager is not None:
            if request.enabled:
                state.vpn_manager.start()
            else:
                state.vpn_manager.stop()
        state.vpn_enabled = bool(request.enabled)
        return _empty_response().SerializeToString(), ()

    if method == "TriggerDownloadGateScan":
        request = waterfall_pb2.DownloadScanRequest()
        request.ParseFromString(payload)
        return _scan_download(request).SerializeToString(), ()

    if method == "RecordPrivacyEvent":
        request = waterfall_pb2.PrivacyEvent()
        request.ParseFromString(payload)
        state.privacy_events.append(request)
        return _empty_response().SerializeToString(), ()

    if method == "CheckForUpdates":
        return _build_update_manifest().SerializeToString(), ()

    if method == "ApplyUpdate":
        return _empty_response().SerializeToString(), ("update-apply-bootstrap",)

    raise KeyError(method)


def _handle_connection(connection: socket.socket, state: OrchestratorState) -> None:
    handshake_payload = _read_frame(connection)
    if handshake_payload is None:
        return

    handshake_request = waterfall_pb2.BridgeHandshakeRequest()
    handshake_request.ParseFromString(handshake_payload)
    handshake_response = _build_handshake_response(handshake_request)
    _write_frame(connection, handshake_response.SerializeToString())

    if not handshake_response.accepted:
        return

    granted = set(handshake_response.granted_capabilities)

    while True:
        frame = _read_frame(connection)
        if frame is None:
            return

        envelope = waterfall_pb2.BridgeRequestEnvelope()
        envelope.ParseFromString(frame)
        response = waterfall_pb2.BridgeResponseEnvelope(
            request_id=envelope.request_id,
            method=envelope.method,
        )

        if any(capability not in granted for capability in envelope.capabilities):
            response.ok = False
            response.error_code = "capability-denied"
            response.error_message = "WaterFall orchestrator denied a capability-scoped request."
            _write_frame(connection, response.SerializeToString())
            continue

        try:
            payload, warnings = _handle_method(envelope.method, envelope.payload, state)
            response.ok = True
            response.payload = payload
            response.warnings.extend(warnings)
        except KeyError:
            response.ok = False
            response.error_code = "method-not-supported"
            response.error_message = f"WaterFall orchestrator does not support {envelope.method}."
        except Exception as exc:  # pragma: no cover - defensive boundary
            response.ok = False
            response.error_code = "internal-error"
            response.error_message = str(exc)

        _write_frame(connection, response.SerializeToString())


def _create_listener(endpoint: TcpLoopbackEndpoint | UnixSocketEndpoint) -> socket.socket:
    if isinstance(endpoint, TcpLoopbackEndpoint):
        listener = socket.create_server((endpoint.host, endpoint.port), family=socket.AF_INET, backlog=1)
        listener.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return listener

    socket_path = Path(endpoint.path)
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    if socket_path.exists():
        socket_path.unlink()

    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(str(socket_path))
    listener.listen(1)

    def _cleanup_socket() -> None:
        if socket_path.exists():
            socket_path.unlink()

    atexit.register(_cleanup_socket)
    return listener


def main() -> int:
    endpoint_spec = os.environ.get("WATERFALL_ORCHESTRATOR_ENDPOINT", "").strip()
    if not endpoint_spec:
        raise RuntimeError("WATERFALL_ORCHESTRATOR_ENDPOINT is required.")

    endpoint = _parse_endpoint(endpoint_spec)
    state = _build_initial_state()
    listener = _create_listener(endpoint)

    print(f"[waterfall-orchestrator] listening on {endpoint_spec}", flush=True)

    try:
        while True:
            connection, _address = listener.accept()
            with connection:
                connection.settimeout(None)
                _handle_connection(connection, state)
    except KeyboardInterrupt:
        return 0
    finally:
        listener.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
