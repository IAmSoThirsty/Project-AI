"""
Coverage-boost tests for src/app/core/secure_comms.py.

Covers: dataclass construction, SecureCommunicationsKernel init / lifecycle,
cryptographic operations, rate limiting, anti-replay, metrics, and routing.
"""

import secrets
import tempfile

import pytest

from app.core.secure_comms import (
    ByzantineVote,
    MessagePriority,
    MessageStatus,
    RouteEntry,
    SecureCommunicationsKernel,
    SecureMessage,
    TransportEndpoint,
    TransportType,
)


# ── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def kernel(tmp_dir):
    """Non-started kernel for unit tests (no background threads)."""
    return SecureCommunicationsKernel(data_dir=tmp_dir)


@pytest.fixture
def started_kernel(tmp_dir):
    """Kernel with workers started; shut down at end."""
    k = SecureCommunicationsKernel(data_dir=tmp_dir)
    k.initialize()
    yield k
    k.shutdown()


# ── enums ───────────────────────────────────────────────────────────────────


class TestEnums:
    def test_transport_types(self):
        assert TransportType.TCP.value == "tcp"
        assert TransportType.STORE_FORWARD.value == "store_forward"

    def test_message_priority(self):
        assert MessagePriority.CRITICAL.value == 0
        assert MessagePriority.BACKGROUND.value == 4

    def test_message_status(self):
        assert MessageStatus.PENDING.value == "pending"
        assert MessageStatus.EXPIRED.value == "expired"


# ── dataclasses ─────────────────────────────────────────────────────────────


class TestDataclasses:
    def test_secure_message(self):
        msg = SecureMessage(
            message_id="m1",
            sender_id="s",
            recipient_id="r",
            payload=b"data",
            signature=b"sig",
            hmac_digest=b"hmac",
            timestamp=1234567890.0,
            priority=MessagePriority.NORMAL,
        )
        assert msg.ttl == 86400
        assert len(msg.nonce) == 24

    def test_transport_endpoint(self):
        ep = TransportEndpoint(
            endpoint_id="e1",
            transport_type=TransportType.TCP,
            address="127.0.0.1",
            port=8080,
        )
        assert ep.reliability == 0.99
        assert ep.enabled

    def test_route_entry(self):
        re = RouteEntry(
            destination_id="d1",
            next_hop_id="n1",
            hop_count=2,
            latency_ms=15.0,
            reliability=0.95,
            last_updated=1234.0,
            transport_type=TransportType.UDP,
        )
        assert re.hop_count == 2

    def test_byzantine_vote(self):
        bv = ByzantineVote(
            voter_id="v1",
            proposal_id="p1",
            vote=True,
            timestamp=1234.0,
            signature=b"sig",
        )
        assert bv.vote


# ── kernel construction ─────────────────────────────────────────────────────


class TestKernelConstruction:
    def test_node_id_generated(self, kernel):
        assert len(kernel.node_id) == 16

    def test_keys_generated(self, kernel):
        assert kernel.identity_private_key is not None
        assert kernel.identity_public_key is not None
        assert kernel.ephemeral_private_key is not None
        assert kernel.ephemeral_public_key is not None

    def test_queues_initialized(self, kernel):
        assert kernel.outbound_queue.empty()
        assert kernel.inbound_queue.empty()

    def test_metrics_initialized(self, kernel):
        assert kernel.metrics["messages_sent"] == 0
        assert kernel.metrics["messages_received"] == 0

    def test_subsystem_metadata(self, kernel):
        meta = kernel.SUBSYSTEM_METADATA
        assert meta["id"] == "secure_comms_kernel"
        assert "encrypted_messaging" in meta["provides_capabilities"]


# ── lifecycle ───────────────────────────────────────────────────────────────


class TestKernelLifecycle:
    def test_initialize_and_shutdown(self, tmp_dir):
        k = SecureCommunicationsKernel(data_dir=tmp_dir)
        assert k.initialize()
        assert k.running
        assert k.shutdown()
        assert not k.running

    def test_health_check_not_initialized(self, kernel):
        assert not kernel.health_check()

    def test_health_check_initialized(self, started_kernel):
        assert started_kernel.health_check()

    def test_get_status(self, kernel):
        status = kernel.get_status()
        assert "node_id" in status
        assert "metrics" in status
        assert status["pending_messages"] == 0


# ── cryptographic operations ────────────────────────────────────────────────


class TestCryptoOperations:
    def test_sign_message(self, kernel):
        msg = b"test message"
        sig = kernel._sign_message(msg)
        assert len(sig) == 64

    def test_sign_verify_roundtrip(self, kernel):
        from cryptography.hazmat.primitives import serialization

        msg = b"verify me"
        sig = kernel._sign_message(msg)
        pub_bytes = kernel.identity_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        assert kernel._verify_signature(msg, sig, pub_bytes)

    def test_verify_bad_signature(self, kernel):
        from cryptography.hazmat.primitives import serialization

        msg = b"message"
        bad_sig = b"\x00" * 64
        pub_bytes = kernel.identity_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        assert not kernel._verify_signature(msg, bad_sig, pub_bytes)

    def test_encrypt_decrypt_roundtrip(self, tmp_dir):
        from cryptography.hazmat.primitives import serialization

        k1 = SecureCommunicationsKernel(data_dir=tmp_dir + "/k1")
        k2 = SecureCommunicationsKernel(data_dir=tmp_dir + "/k2")

        # k1 encrypts for k2 using k2's ephemeral public key
        k2_pub = k2.ephemeral_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        plaintext = b"secret data"
        ciphertext, nonce = k1._encrypt_message(plaintext, k2_pub)
        assert ciphertext != plaintext

        # k2 decrypts using k1's ephemeral public key
        k1_pub = k1.ephemeral_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        decrypted = k2._decrypt_message(ciphertext, nonce, k1_pub)
        assert decrypted == plaintext

    def test_decrypt_bad_data(self, kernel):
        result = kernel._decrypt_message(b"bad", b"x" * 12, b"z" * 32)
        assert result is None

    def test_compute_hmac(self, kernel):
        key = secrets.token_bytes(32)
        h = kernel._compute_hmac(b"data", key)
        assert len(h) == 64  # SHA-512 produces 64 bytes

    def test_encryption_increments_metric(self, tmp_dir):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import x25519

        k = SecureCommunicationsKernel(data_dir=tmp_dir)
        peer_key = x25519.X25519PrivateKey.generate().public_key()
        peer_bytes = peer_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        before = k.metrics["encryption_operations"]
        k._encrypt_message(b"test", peer_bytes)
        assert k.metrics["encryption_operations"] == before + 1


# ── anti-replay ─────────────────────────────────────────────────────────────


class TestAntiReplay:
    def test_seen_nonces_deque(self, kernel):
        assert len(kernel.seen_nonces) == 0
        kernel.seen_nonces.append(b"nonce1")
        assert len(kernel.seen_nonces) == 1

    def test_nonce_maxlen(self, kernel):
        for i in range(10001):
            kernel.seen_nonces.append(i)
        assert len(kernel.seen_nonces) == 10000


# ── rate limiting ───────────────────────────────────────────────────────────


class TestRateLimiting:
    def test_rate_limit_default(self, kernel):
        assert kernel.rate_limit_max == 100
        assert kernel.rate_limit_window == 60


# ── database ────────────────────────────────────────────────────────────────


class TestDatabase:
    def test_db_tables_created(self, kernel):
        import sqlite3

        conn = sqlite3.connect(kernel.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        assert "messages" in tables
        assert "routing_table" in tables
        assert "peer_keys" in tables


# ── consensus ───────────────────────────────────────────────────────────────


class TestConsensus:
    def test_consensus_quorum(self, kernel):
        assert kernel.consensus_quorum == pytest.approx(0.67)

    def test_consensus_votes_storage(self, kernel):
        kernel.consensus_votes["proposal_1"].append(
            ByzantineVote(
                voter_id="v1",
                proposal_id="proposal_1",
                vote=True,
                timestamp=1234.0,
                signature=b"sig",
            )
        )
        assert len(kernel.consensus_votes["proposal_1"]) == 1

    def test_check_consensus_no_votes(self, kernel):
        assert kernel.check_consensus("unknown") is None

    def test_check_consensus_reached(self, kernel):
        for i in range(3):
            kernel.consensus_votes["p1"].append(
                ByzantineVote(
                    voter_id=f"v{i}", proposal_id="p1", vote=True,
                    timestamp=1234.0, signature=b"sig",
                )
            )
        assert kernel.check_consensus("p1") is True

    def test_check_consensus_rejected(self, kernel):
        for i in range(3):
            kernel.consensus_votes["p2"].append(
                ByzantineVote(
                    voter_id=f"v{i}", proposal_id="p2", vote=False,
                    timestamp=1234.0, signature=b"sig",
                )
            )
        assert kernel.check_consensus("p2") is False

    def test_check_consensus_split(self, kernel):
        kernel.consensus_votes["p3"].append(
            ByzantineVote(
                voter_id="v0", proposal_id="p3", vote=True,
                timestamp=1234.0, signature=b"sig",
            )
        )
        kernel.consensus_votes["p3"].append(
            ByzantineVote(
                voter_id="v1", proposal_id="p3", vote=False,
                timestamp=1234.0, signature=b"sig",
            )
        )
        result = kernel.check_consensus("p3")
        assert result is False  # 50% yes < 67% quorum, and 50% no > 33%

    def test_propose_consensus(self, kernel):
        ok = kernel.propose_consensus("prop1", {"key": "value"})
        assert ok
        assert kernel.metrics["consensus_rounds"] == 1
        assert len(kernel.consensus_votes["prop1"]) == 1


# ── message handling ────────────────────────────────────────────────────────


class TestMessageHandling:
    def test_send_message(self, kernel):
        ok = kernel.send_message("dest_node", {"hello": "world"})
        assert ok
        assert kernel.metrics["messages_sent"] == 1

    def test_send_message_string(self, kernel):
        ok = kernel.send_message("dest", "plain text")
        assert ok

    def test_send_message_bytes(self, kernel):
        ok = kernel.send_message("dest", b"raw bytes")
        assert ok

    def test_receive_messages_empty(self, kernel):
        msgs = kernel.receive_messages()
        assert msgs == []

    def test_broadcast_no_neighbors(self, kernel):
        count = kernel.broadcast({"msg": "hi"})
        assert count == 0


# ── transport ───────────────────────────────────────────────────────────────


class TestTransport:
    def test_register_transport(self, kernel):
        ep = TransportEndpoint(
            endpoint_id="ep1",
            transport_type=TransportType.TCP,
            address="127.0.0.1",
            port=9090,
        )
        assert kernel.register_transport(ep)
        assert "ep1" in kernel.transports

    def test_transmit_store_forward(self, kernel):
        msg = SecureMessage(
            message_id="m1", sender_id="s", recipient_id="r",
            payload=b"data", signature=b"sig", hmac_digest=b"hmac",
            timestamp=1234.0, priority=MessagePriority.NORMAL,
        )
        ep = TransportEndpoint(
            endpoint_id="sf", transport_type=TransportType.STORE_FORWARD,
            address="localhost",
        )
        ok = kernel._transmit_store_forward(msg, ep)
        assert ok
        assert len(kernel.store_forward_queue) == 1

    def test_select_best_transport_empty(self, kernel):
        route = RouteEntry(
            destination_id="d", next_hop_id="n", hop_count=1,
            latency_ms=10.0, reliability=0.99, last_updated=1234.0,
            transport_type=TransportType.TCP,
        )
        assert kernel._select_best_transport(route) is None

    def test_select_best_transport_matching(self, kernel):
        ep = TransportEndpoint(
            endpoint_id="tcp1", transport_type=TransportType.TCP,
            address="127.0.0.1", port=8080,
        )
        kernel.register_transport(ep)
        route = RouteEntry(
            destination_id="d", next_hop_id="n", hop_count=1,
            latency_ms=10.0, reliability=0.99, last_updated=1234.0,
            transport_type=TransportType.TCP,
        )
        result = kernel._select_best_transport(route)
        assert result.endpoint_id == "tcp1"


# ── serialization ───────────────────────────────────────────────────────────


class TestSerialization:
    def test_serialize_deserialize_roundtrip(self, kernel):
        msg = SecureMessage(
            message_id="m1", sender_id="s", recipient_id="r",
            payload=b"hello", signature=b"\x01" * 64,
            hmac_digest=b"\x02" * 64, timestamp=1234.0,
            priority=MessagePriority.HIGH, nonce=b"\x03" * 24,
        )
        data = kernel._serialize_message(msg)
        restored = kernel._deserialize_message(data)
        assert restored is not None
        assert restored.message_id == "m1"
        assert restored.payload == b"hello"

    def test_deserialize_bad_data(self, kernel):
        assert kernel._deserialize_message(b"not json") is None


# ── routing ─────────────────────────────────────────────────────────────────


class TestRouting:
    def test_update_routing_table(self, kernel):
        route = RouteEntry(
            destination_id="d1", next_hop_id="n1", hop_count=2,
            latency_ms=15.0, reliability=0.95, last_updated=1234.0,
            transport_type=TransportType.UDP,
        )
        assert kernel.update_routing_table(route)
        assert "d1" in kernel.routing_table

    def test_find_route_neighbor(self, kernel):
        kernel.neighbor_nodes.add("neighbor1")
        route = kernel.find_route("neighbor1")
        assert route is not None
        assert route.hop_count == 1

    def test_find_route_table(self, kernel):
        route = RouteEntry(
            destination_id="remote", next_hop_id="hop1", hop_count=3,
            latency_ms=50.0, reliability=0.9, last_updated=1234.0,
            transport_type=TransportType.TCP,
        )
        kernel.update_routing_table(route)
        found = kernel.find_route("remote")
        assert found.hop_count == 3

    def test_find_route_not_found(self, kernel):
        assert kernel.find_route("nowhere") is None


# ── rate limiting ───────────────────────────────────────────────────────────


class TestRateLimiting:
    def test_rate_limit_allowed(self, kernel):
        assert kernel._check_rate_limit("peer1")

    def test_rate_limit_exceeded(self, kernel):
        kernel.rate_limit_max = 3
        for _ in range(3):
            kernel._check_rate_limit("peer2")
        assert not kernel._check_rate_limit("peer2")


# ── configuration ───────────────────────────────────────────────────────────


class TestConfiguration:
    def test_get_config(self, kernel):
        cfg = kernel.get_config()
        assert "node_id" in cfg
        assert "consensus_quorum" in cfg

    def test_set_config(self, kernel):
        ok = kernel.set_config({"rate_limit_max": 200})
        assert ok
        assert kernel.rate_limit_max == 200

    def test_validate_config_ok(self, kernel):
        ok, msg = kernel.validate_config({"consensus_quorum": 0.75})
        assert ok and msg is None

    def test_validate_config_bad(self, kernel):
        ok, msg = kernel.validate_config({"consensus_quorum": 0.3})
        assert not ok
        assert "0.5" in msg


# ── events ──────────────────────────────────────────────────────────────────


class TestEvents:
    def test_subscribe_and_emit(self, kernel):
        received = []
        sub_id = kernel.subscribe("test_event", lambda d: received.append(d))
        kernel.emit_event("test_event", {"key": "val"})
        assert len(received) == 1

    def test_unsubscribe(self, kernel):
        received = []
        sub_id = kernel.subscribe("ev", lambda d: received.append(d))
        kernel.unsubscribe(sub_id)
        kernel.emit_event("ev", {})
        assert len(received) == 0

    def test_emit_no_subscribers(self, kernel):
        count = kernel.emit_event("nobody_listening", {})
        assert count == 0


# ── metrics ─────────────────────────────────────────────────────────────────


class TestMetrics:
    def test_get_metrics(self, kernel):
        m = kernel.get_metrics()
        assert "messages_sent" in m

    def test_get_metric(self, kernel):
        assert kernel.get_metric("messages_sent") == 0
        assert kernel.get_metric("nonexistent") is None

    def test_reset_metrics(self, kernel):
        kernel.metrics["messages_sent"] = 42
        kernel.reset_metrics()
        assert kernel.metrics["messages_sent"] == 0


# ── security interface ──────────────────────────────────────────────────────


class TestSecurityInterface:
    def test_authenticate(self, kernel):
        assert kernel.authenticate({})

    def test_authorize(self, kernel):
        assert kernel.authorize("any_action", {})

    def test_audit_log(self, kernel):
        assert kernel.audit_log("test", {"detail": "value"})


# ── persistence ─────────────────────────────────────────────────────────────


class TestPersistence:
    def test_persist_message(self, kernel):
        msg = SecureMessage(
            message_id="pm1", sender_id="s", recipient_id="r",
            payload=b"data", signature=b"sig", hmac_digest=b"hmac",
            timestamp=1234.0, priority=MessagePriority.NORMAL,
        )
        kernel._persist_message(msg)
        import sqlite3
        conn = sqlite3.connect(kernel.db_path)
        cur = conn.cursor()
        cur.execute("SELECT message_id FROM messages WHERE message_id='pm1'")
        assert cur.fetchone() is not None
        conn.close()

    def test_persist_route(self, kernel):
        route = RouteEntry(
            destination_id="pr1", next_hop_id="n", hop_count=1,
            latency_ms=10.0, reliability=0.99, last_updated=1234.0,
            transport_type=TransportType.TCP,
        )
        kernel._persist_route(route)
        import sqlite3
        conn = sqlite3.connect(kernel.db_path)
        cur = conn.cursor()
        cur.execute("SELECT destination_id FROM routing_table WHERE destination_id='pr1'")
        assert cur.fetchone() is not None
        conn.close()
