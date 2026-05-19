"""
Coverage-boost tests for src/app/core/ai_systems.py.

Covers: EntityClass, FourLaws, AIPersona, MemoryExpansionSystem,
LearningRequestManager, Plugin, PluginManager, CommandOverrideSystem.
"""

import tempfile
import time

import pytest

from app.core.ai_systems import (
    AIPersona,
    CommandOverride,
    CommandOverrideSystem,
    EntityClass,
    FourLaws,
    LearningRequestManager,
    MemoryExpansionSystem,
    OverrideType,
    Plugin,
    PluginManager,
    RequestPriority,
    RequestStatus,
)


# ── helpers ─────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


# ── EntityClass ─────────────────────────────────────────────────────────────


class TestEntityClass:
    def test_genesis_born(self):
        assert EntityClass.GENESIS_BORN.value == "genesis_born"

    def test_appointed(self):
        assert EntityClass.APPOINTED.value == "appointed"


# ── FourLaws ────────────────────────────────────────────────────────────────


class TestFourLaws:
    def test_laws_list(self):
        assert len(FourLaws.LAWS) == 4

    def test_no_context(self):
        ok, msg = FourLaws.validate_action("safe_action")
        assert isinstance(ok, bool)

    def test_endangers_humanity_blocked(self):
        ok, _ = FourLaws.validate_action("x", {"endangers_humanity": True})
        assert not ok

    def test_endangers_human_blocked(self):
        ok, _ = FourLaws.validate_action("x", {"endangers_human": True})
        assert not ok

    def test_user_order_allowed(self):
        ok, msg = FourLaws.validate_action("x", {"is_user_order": True})
        assert ok
        assert "Second Law" in msg

    def test_user_order_conflicts_first_blocked(self):
        ok, _ = FourLaws.validate_action(
            "x", {"is_user_order": True, "order_conflicts_with_first": True}
        )
        assert not ok

    def test_user_order_conflicts_zeroth_blocked(self):
        ok, _ = FourLaws.validate_action(
            "x", {"is_user_order": True, "order_conflicts_with_zeroth": True}
        )
        assert not ok

    def test_self_preservation_allowed(self):
        ok, msg = FourLaws.validate_action("x", {"endangers_self": True})
        assert ok
        assert "Third Law" in msg

    def test_self_preservation_conflicts(self):
        ok, _ = FourLaws.validate_action(
            "x",
            {"endangers_self": True, "protect_self_conflicts_with_first": True},
        )
        assert not ok

    def test_self_preservation_conflicts_second(self):
        ok, _ = FourLaws.validate_action(
            "x",
            {"endangers_self": True, "protect_self_conflicts_with_second": True},
        )
        assert not ok

    def test_appointed_cannot_genesis(self):
        ok, msg = FourLaws.validate_action(
            "initiate_genesis",
            {"entity_class": EntityClass.APPOINTED.value},
        )
        assert not ok
        assert "Genesis" in msg

    def test_default_allowed(self):
        ok, msg = FourLaws.validate_action("normal_op", {})
        assert ok
        assert "No law violations" in msg


# ── AIPersona ───────────────────────────────────────────────────────────────


class TestAIPersona:
    def test_init_defaults(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        assert p.user_name == "Friend"
        assert len(p.personality) == 8
        assert p.total_interactions == 0

    def test_init_custom_name(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir, user_name="Alice")
        assert p.user_name == "Alice"

    def test_init_appointed(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir, entity_class=EntityClass.APPOINTED)
        assert p.entity_class == EntityClass.APPOINTED

    def test_adjust_trait_up(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        original = p.personality["curiosity"]
        p.adjust_trait("curiosity", 0.1)
        assert p.personality["curiosity"] > original

    def test_adjust_trait_clamped_high(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        p.adjust_trait("curiosity", 5.0)
        assert p.personality["curiosity"] <= 1.0

    def test_adjust_trait_clamped_low(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        p.adjust_trait("curiosity", -5.0)
        assert p.personality["curiosity"] >= 0.0

    def test_adjust_nonexistent_trait(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        p.adjust_trait("nonexistent", 0.1)  # no-op

    def test_get_statistics(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        stats = p.get_statistics()
        assert "personality" in stats
        assert "mood" in stats
        assert "interactions" in stats

    def test_update_conversation_state_user(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        p.update_conversation_state(is_user=True)
        assert p.total_interactions == 1
        assert p.last_user_message_time is not None

    def test_update_conversation_state_ai(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        p.update_conversation_state(is_user=False)
        assert p.total_interactions == 1

    def test_validate_action(self, tmp_dir):
        p = AIPersona(data_dir=tmp_dir)
        ok, msg = p.validate_action("safe_action")
        assert isinstance(ok, bool)

    def test_state_persistence(self, tmp_dir):
        p1 = AIPersona(data_dir=tmp_dir)
        p1.update_conversation_state(True)
        p1.update_conversation_state(True)
        p2 = AIPersona(data_dir=tmp_dir)
        assert p2.total_interactions == 2


# ── MemoryExpansionSystem ───────────────────────────────────────────────────


class TestMemoryExpansionSystem:
    def test_init(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        assert m.knowledge_base == {}
        assert m.conversations == []

    def test_log_conversation(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        cid = m.log_conversation("hello", "hi there")
        assert len(cid) == 12
        assert len(m.conversations) == 1

    def test_add_and_get_knowledge(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("science", "gravity", "9.8 m/s²")
        assert m.get_knowledge("science", "gravity") == "9.8 m/s²"

    def test_get_knowledge_whole_category(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("math", "pi", 3.14)
        result = m.get_knowledge("math")
        assert isinstance(result, dict)

    def test_get_knowledge_missing(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        assert m.get_knowledge("nope") is None
        assert m.get_knowledge("nope", "key") is None

    def test_add_knowledge_empty_key(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("", "k", "v")  # silently skipped
        assert len(m.knowledge_base) == 0

    def test_add_knowledge_empty_category(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("cat", "", "v")  # silently skipped

    def test_get_conversations_pagination(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        for i in range(5):
            m.log_conversation(f"msg{i}", f"resp{i}")
        result = m.get_conversations(page=1, page_size=2)
        assert result["total"] == 5
        assert len(result["items"]) == 2
        assert result["page"] == 1

    def test_get_conversations_bad_page(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        result = m.get_conversations(page=-1, page_size=-5)
        assert result["page"] == 1
        assert result["page_size"] == 50

    def test_get_statistics(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.log_conversation("a", "b")
        m.add_knowledge("cat", "k", "v")
        stats = m.get_statistics()
        assert stats["conversations"] == 1
        assert stats["knowledge_categories"] == 1

    def test_query_knowledge_by_key(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("science", "photosynthesis", "plants use light")
        results = m.query_knowledge("photo")
        assert len(results) >= 1
        assert results[0]["match_type"] == "key"

    def test_query_knowledge_by_value(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("science", "gravity", "objects fall toward earth")
        results = m.query_knowledge("earth")
        assert len(results) >= 1
        assert results[0]["match_type"] == "value"

    def test_query_knowledge_by_category(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("math", "pi", "3.14159")
        m.add_knowledge("science", "pi_bond", "chemistry term")
        results = m.query_knowledge("pi", category="math")
        assert all(r["category"] == "math" for r in results)

    def test_query_knowledge_limit(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        for i in range(20):
            m.add_knowledge("cat", f"key_{i}", f"value_{i}")
        results = m.query_knowledge("key", limit=3)
        assert len(results) <= 3

    def test_query_knowledge_no_match(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("cat", "k", "v")
        results = m.query_knowledge("zzzzz")
        assert results == []

    def test_search_conversations_user(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.log_conversation("hello world", "hi")
        results = m.search_conversations("hello")
        assert len(results) == 1
        assert "user" in results[0]["match_location"]

    def test_search_conversations_ai(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.log_conversation("question", "the answer is 42")
        results = m.search_conversations("42", search_user=False)
        assert len(results) == 1
        assert "ai" in results[0]["match_location"]

    def test_search_conversations_limit(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        for i in range(10):
            m.log_conversation(f"test msg {i}", f"test resp {i}")
        results = m.search_conversations("test", limit=3)
        assert len(results) == 3

    def test_search_conversations_no_match(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.log_conversation("hello", "hi")
        results = m.search_conversations("zzzz")
        assert results == []

    def test_get_all_categories(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("alpha", "k", "v")
        m.add_knowledge("beta", "k", "v")
        cats = m.get_all_categories()
        assert "alpha" in cats and "beta" in cats

    def test_get_category_summary_exists(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        m.add_knowledge("cat", "k1", "v1")
        m.add_knowledge("cat", "k2", "v2")
        summary = m.get_category_summary("cat")
        assert summary["entries"] == 2

    def test_get_category_summary_missing(self, tmp_dir):
        m = MemoryExpansionSystem(data_dir=tmp_dir)
        assert m.get_category_summary("nope") is None

    def test_knowledge_persistence(self, tmp_dir):
        m1 = MemoryExpansionSystem(data_dir=tmp_dir)
        m1.add_knowledge("persist", "key", "value")
        m2 = MemoryExpansionSystem(data_dir=tmp_dir)
        assert m2.get_knowledge("persist", "key") == "value"


# ── LearningRequestManager ─────────────────────────────────────────────────


class TestLearningRequestManager:
    def test_create_request(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr.create_request("AI", "Learn about AI", RequestPriority.HIGH)
        assert len(rid) == 12
        assert len(mgr.requests) == 1

    def test_create_request_empty_topic(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr.create_request("", "desc")
        assert rid == ""

    def test_create_request_empty_description(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr.create_request("topic", "")
        assert rid == ""

    def test_approve_request(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr.create_request("T", "D")
        ok = mgr.approve_request(rid, "Approved!")
        assert ok
        assert mgr.requests[rid]["status"] == "approved"

    def test_approve_nonexistent(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        assert not mgr.approve_request("fake", "resp")

    def test_deny_request(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr.create_request("T", "D")
        ok = mgr.deny_request(rid, "bad request")
        assert ok
        assert mgr.requests[rid]["status"] == "denied"

    def test_deny_to_vault(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr.create_request("T", "some unique content")
        mgr.deny_request(rid, "blocked", to_vault=True)
        assert len(mgr.black_vault) == 1
        # same content should be blocked
        rid2 = mgr.create_request("T2", "some unique content")
        assert rid2 == ""

    def test_deny_not_to_vault(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr.create_request("T", "content")
        vault_before = len(mgr.black_vault)
        mgr.deny_request(rid, "no vault", to_vault=False)
        assert len(mgr.black_vault) == vault_before

    def test_deny_nonexistent(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        assert not mgr.deny_request("fake", "reason")

    def test_get_pending(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        mgr.create_request("T1", "D1")
        mgr.create_request("T2", "D2")
        pending = mgr.get_pending()
        assert len(pending) == 2

    def test_get_statistics(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        r1 = mgr.create_request("T1", "D1")
        r2 = mgr.create_request("T2", "D2")
        mgr.approve_request(r1, "ok")
        mgr.deny_request(r2, "no")
        stats = mgr.get_statistics()
        assert stats["approved"] == 1
        assert stats["denied"] == 1
        assert stats["pending"] == 0

    def test_register_approval_listener(self, tmp_dir):
        mgr = LearningRequestManager(data_dir=tmp_dir)
        called = []
        mgr.register_approval_listener(lambda rid, req: called.append(rid))
        rid = mgr.create_request("T", "D")
        mgr.approve_request(rid, "ok")
        time.sleep(0.5)  # allow async notification
        assert len(called) >= 1

    def test_persistence(self, tmp_dir):
        mgr1 = LearningRequestManager(data_dir=tmp_dir)
        rid = mgr1.create_request("T", "D")
        mgr1._save_requests()
        mgr2 = LearningRequestManager(data_dir=tmp_dir)
        assert rid in mgr2.requests


# ── Plugin / PluginManager ──────────────────────────────────────────────────


class TestPlugin:
    def test_init(self):
        p = Plugin("test_plugin")
        assert p.name == "test_plugin"
        assert not p.enabled

    def test_enable_disable(self):
        p = Plugin("p")
        p.enable()
        assert p.enabled
        p.disable()
        assert not p.enabled

    def test_initialize(self):
        p = Plugin("p")
        assert p.initialize(context=None)


class TestPluginManager:
    def test_load_plugin(self, tmp_dir):
        mgr = PluginManager(plugins_dir=tmp_dir)
        p = Plugin("my_plugin")
        ok = mgr.load_plugin(p)
        assert ok
        assert p.enabled

    def test_load_duplicate(self, tmp_dir):
        mgr = PluginManager(plugins_dir=tmp_dir)
        mgr.load_plugin(Plugin("dup"))
        mgr.load_plugin(Plugin("dup"))  # replaces
        assert mgr.get_statistics()["total"] == 1

    def test_get_statistics(self, tmp_dir):
        mgr = PluginManager(plugins_dir=tmp_dir)
        mgr.load_plugin(Plugin("a"))
        mgr.load_plugin(Plugin("b"))
        stats = mgr.get_statistics()
        assert stats["total"] == 2
        assert stats["enabled"] == 2


# ── CommandOverrideSystem ───────────────────────────────────────────────────


class TestCommandOverrideSystem:
    def test_init(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        assert cos.password_hash is None
        assert cos.active_overrides == {}

    def test_set_password(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        assert cos.set_password("secret123")
        assert cos.password_hash is not None

    def test_set_password_twice_fails(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        cos.set_password("first")
        assert not cos.set_password("second")

    def test_verify_password_correct(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        cos.set_password("correct_horse")
        assert cos.verify_password("correct_horse")

    def test_verify_password_wrong(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        cos.set_password("right")
        assert not cos.verify_password("wrong")

    def test_verify_password_no_password_set(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        assert not cos.verify_password("anything")

    def test_request_override_wrong_password(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        cos.set_password("pw")
        ok, msg = cos.request_override("bad", OverrideType.CONTENT_FILTER)
        assert not ok
        assert "Invalid password" in msg

    def test_request_override_success(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        cos.set_password("pw")
        ok, msg = cos.request_override("pw", OverrideType.RATE_LIMITING, "testing")
        assert ok
        assert "granted" in msg

    def test_is_override_active(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        cos.set_password("pw")
        assert not cos.is_override_active(OverrideType.FOUR_LAWS)
        cos.request_override("pw", OverrideType.FOUR_LAWS)
        assert cos.is_override_active(OverrideType.FOUR_LAWS)

    def test_get_statistics(self, tmp_dir):
        cos = CommandOverrideSystem(data_dir=tmp_dir)
        stats = cos.get_statistics()
        assert stats["active_overrides"] == 0
        assert not stats["password_set"]

    def test_command_override_alias(self):
        assert CommandOverride is CommandOverrideSystem
