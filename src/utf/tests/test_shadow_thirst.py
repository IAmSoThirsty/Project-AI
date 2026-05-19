"""Shadow Thirst — full conformance test suite.

Covers all 11 analyzers and new language constructs:
  Critical:
    1.  PlaneIsolationAnalyzer
    2.  DeterminismAnalyzer
    3.  PuritySpringAnalyzer
    4.  CanonicalConvergenceAnalyzer
    5.  PrivilegeEscalationAnalyzer
    6.  DeadShadowAnalyzer           (new)
  Warning:
    7.  ResourceEstimator
    8.  MemoryEvaporationAnalyzer
    9.  DivergenceRiskAnalyzer
    10. SectionOrderAnalyzer         (new)
    11. InvariantCompletenessAnalyzer (new)

  Language:
    - on_reject { } block
    - module-level invariant declarations
    - atomic { } groups
    - replay_hash content sensitivity
    - promote_atomic
"""
import unittest

from shadow_thirst.core import (
    AnalysisResult,
    AtomicGroup,
    MutationDecl,
    ShadowModule,
    analyze,
    parse_shadow,
    promote,
    promote_atomic,
    replay_hash,
    visualize,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _promote(src: str) -> str:
    return promote(parse_shadow(src))["verdict"]


def _result(src: str, analyzer: str) -> AnalysisResult:
    results = analyze(parse_shadow(src))
    for r in results:
        if r.analyzer == analyzer:
            return r
    raise AssertionError(f"analyzer '{analyzer}' not in results")


def _passed(src: str, analyzer: str) -> bool:
    return _result(src, analyzer).passed


# ── 1. PlaneIsolationAnalyzer ─────────────────────────────────────────────────

class TestPlaneIsolation(unittest.TestCase):

    def test_clean_shadow_passes(self):
        src = """
mutation validated_canonical clean(val: Int) {
  shadow { drink mut x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_x = val; }
}
"""
        self.assertTrue(_passed(src, "PlaneIsolationAnalyzer"))

    def test_direct_canonical_write_rejected(self):
        src = """
mutation validated_canonical bad(val: Int) {
  shadow { drink canonical_x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_x = val; }
}
"""
        self.assertFalse(_passed(src, "PlaneIsolationAnalyzer"))
        self.assertEqual(_promote(src), "REJECT")

    def test_canonical_write_inside_thirst_block_rejected(self):
        """Bypass attempt: wrap canonical_ write in a thirst block."""
        src = """
mutation validated_canonical sneaky(val: Int) {
  shadow {
    thirst (val > 0) {
      drink canonical_val: Int = val;
    }
  }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        self.assertFalse(_passed(src, "PlaneIsolationAnalyzer"))
        self.assertEqual(_promote(src), "REJECT")


# ── 2. DeterminismAnalyzer ────────────────────────────────────────────────────

class TestDeterminism(unittest.TestCase):

    def test_deterministic_shadow_passes(self):
        src = """
mutation validated_canonical det(val: Int) {
  shadow { drink x: Int = val + 1; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        self.assertTrue(_passed(src, "DeterminismAnalyzer"))

    def test_now_call_rejected(self):
        src = """
mutation validated_canonical ts() {
  shadow { drink t: Any = now(); }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_t = 0; }
}
"""
        self.assertFalse(_passed(src, "DeterminismAnalyzer"))
        self.assertEqual(_promote(src), "REJECT")

    def test_rand_inside_loop_rejected(self):
        """Bypass attempt: hide rand() inside a refill loop."""
        src = """
mutation validated_canonical rng(n: Int) {
  shadow {
    refill 3 times {
      drink r: Int = rand();
    }
  }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_n = n; }
}
"""
        self.assertFalse(_passed(src, "DeterminismAnalyzer"))

    def test_epoch_ms_in_try_block_rejected(self):
        """Bypass attempt: hide nondeterminism in spillage/cleanup."""
        src = """
mutation validated_canonical ts2() {
  shadow {
    spillage {
      drink e: Int = epoch_ms();
    } cleanup error(err: Error) {
      drink ok: Bool = parched;
    }
  }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_e = 0; }
}
"""
        self.assertFalse(_passed(src, "DeterminismAnalyzer"))


# ── 3. PuritySpringAnalyzer ───────────────────────────────────────────────────

class TestPuritySpring(unittest.TestCase):

    def test_pure_invariant_passes(self):
        src = """
mutation validated_canonical pure(n: Int) {
  shadow { drink s: Int = n; }
  invariant { drink check: Bool = n > 0; }
  canonical { canonical_n = n; }
}
"""
        self.assertTrue(_passed(src, "PuritySpringAnalyzer"))

    def test_pour_in_invariant_rejected(self):
        src = """
mutation validated_canonical impure(n: Int) {
  shadow { drink s: Int = n; }
  invariant { pour("checking"); }
  canonical { canonical_n = n; }
}
"""
        self.assertFalse(_passed(src, "PuritySpringAnalyzer"))
        self.assertEqual(_promote(src), "REJECT")

    def test_now_inside_nested_thirst_rejected(self):
        """Bypass attempt: hide impure call inside thirst block."""
        src = """
mutation validated_canonical tricky(n: Int) {
  shadow { drink x: Int = n; }
  invariant {
    thirst (n > 0) {
      drink t: Any = now();
    }
  }
  canonical { canonical_n = n; }
}
"""
        self.assertFalse(_passed(src, "PuritySpringAnalyzer"))


# ── 4. CanonicalConvergenceAnalyzer ──────────────────────────────────────────

class TestCanonicalConvergence(unittest.TestCase):

    def test_shadow_referencing_param_passes(self):
        src = """
mutation validated_canonical converge(value: Int) {
  shadow { drink mut temp: Int = value; temp = temp + 1; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_counter = value; }
}
"""
        self.assertTrue(_passed(src, "CanonicalConvergenceAnalyzer"))

    def test_zero_param_mutation_always_converges(self):
        src = """
mutation validated_canonical zero_param() {
  shadow { drink x: Int = 42; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_x = 1; }
}
"""
        self.assertTrue(_passed(src, "CanonicalConvergenceAnalyzer"))

    def test_shadow_ignoring_all_params_flagged(self):
        src = """
mutation validated_canonical diverge(value: Int) {
  shadow { drink x: Int = 42; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_counter = value; }
}
"""
        self.assertFalse(_passed(src, "CanonicalConvergenceAnalyzer"))
        self.assertEqual(_promote(src), "REJECT")

    def test_param_read_inside_thirst_counts(self):
        """Shadow reading a param inside a thirst block is valid convergence."""
        src = """
mutation validated_canonical conditional(value: Int) {
  shadow {
    thirst (value > 0) {
      drink x: Int = value;
    }
  }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = value; }
}
"""
        self.assertTrue(_passed(src, "CanonicalConvergenceAnalyzer"))


# ── 5. PrivilegeEscalationAnalyzer ───────────────────────────────────────────

class TestPrivilegeEscalation(unittest.TestCase):

    def test_normal_canonical_write_passes(self):
        src = """
mutation validated_canonical normal(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        self.assertTrue(_passed(src, "PrivilegeEscalationAnalyzer"))

    def test_sys_prefix_rejected(self):
        src = """
mutation validated_canonical esc(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { sys_config = val; }
}
"""
        self.assertFalse(_passed(src, "PrivilegeEscalationAnalyzer"))
        self.assertEqual(_promote(src), "REJECT")

    def test_privileged_write_inside_thirst_rejected(self):
        """Bypass attempt: hide privileged write in a thirst block."""
        src = """
mutation validated_canonical bypass(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical {
    thirsty (val > 0) {
      auth_token = val;
    }
  }
}
"""
        self.assertFalse(_passed(src, "PrivilegeEscalationAnalyzer"))

    def test_sovereign_prefix_rejected(self):
        src = """
mutation validated_canonical sov(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { sovereign_key = val; }
}
"""
        self.assertFalse(_passed(src, "PrivilegeEscalationAnalyzer"))


# ── 6. DeadShadowAnalyzer (new) ───────────────────────────────────────────────

class TestDeadShadow(unittest.TestCase):

    def test_active_shadow_passes(self):
        src = """
mutation validated_canonical active(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        self.assertTrue(_passed(src, "DeadShadowAnalyzer"))

    def test_empty_shadow_with_canonical_write_rejected(self):
        src = """
mutation validated_canonical dead(val: Int) {
  shadow { }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        self.assertFalse(_passed(src, "DeadShadowAnalyzer"))
        self.assertEqual(_promote(src), "REJECT")

    def test_empty_shadow_empty_canonical_passes(self):
        """Both empty is fine — no unprotected commit."""
        src = """
mutation validated_canonical noop() {
  shadow { }
  invariant { drink ok: Bool = parched; }
  canonical { }
}
"""
        self.assertTrue(_passed(src, "DeadShadowAnalyzer"))


# ── 7 & 8. ResourceEstimator / MemoryEvaporationAnalyzer ─────────────────────

class TestResourceBudget(unittest.TestCase):

    def test_minimal_shadow_passes_budget(self):
        src = """
mutation validated_canonical minimal() {
  shadow { drink x: Int = 1; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_x = 1; }
}
"""
        self.assertTrue(_passed(src, "ResourceEstimator"))
        self.assertTrue(_passed(src, "MemoryEvaporationAnalyzer"))


# ── 9. DivergenceRiskAnalyzer ─────────────────────────────────────────────────

class TestDivergenceRisk(unittest.TestCase):

    def test_aligned_shadow_passes(self):
        src = """
mutation validated_canonical aligned(value: Int) {
  shadow { drink mut temp: Int = value; temp = temp + 1; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_value = value; }
}
"""
        self.assertTrue(_passed(src, "DivergenceRiskAnalyzer"))

    def test_many_shadow_only_vars_flagged(self):
        src = """
mutation validated_canonical bloated(value: Int) {
  shadow {
    drink a: Int = value;
    drink b: Int = a + 1;
    drink c: Int = b + 2;
    drink d: Int = c * 3;
    drink e: Int = d - value;
  }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_value = value; }
}
"""
        self.assertFalse(_passed(src, "DivergenceRiskAnalyzer"))


# ── 10. SectionOrderAnalyzer (new) ───────────────────────────────────────────

class TestSectionOrder(unittest.TestCase):

    def test_correct_order_passes(self):
        src = """
mutation validated_canonical ordered(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        r = _result(src, "SectionOrderAnalyzer")
        self.assertTrue(r.passed)

    def test_wrong_order_flagged(self):
        # canonical before shadow — parser will accept, analyzer flags
        src = """
mutation validated_canonical misordered(val: Int) {
  canonical { canonical_val = val; }
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
}
"""
        r = _result(src, "SectionOrderAnalyzer")
        self.assertFalse(r.passed)

    def test_on_reject_at_end_passes(self):
        src = """
mutation validated_canonical with_reject(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
  on_reject { pour("rejected"); }
}
"""
        r = _result(src, "SectionOrderAnalyzer")
        self.assertTrue(r.passed)


# ── 11. InvariantCompletenessAnalyzer (new) ───────────────────────────────────

class TestInvariantCompleteness(unittest.TestCase):

    def test_gated_canonical_passes(self):
        src = """
mutation validated_canonical gated(n: Int) {
  shadow { drink x: Int = n; }
  invariant { drink check: Bool = n > 0; }
  canonical { canonical_n = n; }
}
"""
        self.assertTrue(_passed(src, "InvariantCompletenessAnalyzer"))

    def test_two_writes_empty_invariant_flagged(self):
        src = """
mutation validated_canonical ungated(a: Int, b: Int) {
  shadow { drink x: Int = a; drink y: Int = b; }
  invariant { }
  canonical { canonical_a = a; canonical_b = b; }
}
"""
        self.assertFalse(_passed(src, "InvariantCompletenessAnalyzer"))

    def test_single_write_empty_invariant_flagged(self):
        src = """
mutation validated_canonical single_ungated(val: Int) {
  shadow { drink x: Int = val; }
  invariant { }
  canonical { canonical_val = val; }
}
"""
        self.assertFalse(_passed(src, "InvariantCompletenessAnalyzer"))


# ── Language: on_reject block ─────────────────────────────────────────────────

class TestOnReject(unittest.TestCase):

    def test_on_reject_parsed(self):
        src = """
mutation validated_canonical with_handler(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = val > 0; }
  canonical { canonical_val = val; }
  on_reject { pour("mutation withheld by analyzer"); }
}
"""
        module = parse_shadow(src)
        self.assertEqual(len(module.mutations), 1)
        m = module.mutations[0]
        self.assertTrue(len(m.on_reject_body) > 0)
        self.assertIn("on_reject", m.section_order)
        self.assertEqual(m.section_order[-1], "on_reject")

    def test_on_reject_appears_in_section_order(self):
        src = """
mutation validated_canonical tracked(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
  on_reject { pour("withheld"); }
}
"""
        module = parse_shadow(src)
        self.assertEqual(module.mutations[0].section_order,
                         ["shadow", "invariant", "canonical", "on_reject"])


# ── Language: module-level invariants ─────────────────────────────────────────

class TestModuleInvariants(unittest.TestCase):

    def test_module_invariant_parsed(self):
        src = """
invariant positive(n: Int) {
  drink check: Bool = n > 0;
}

mutation validated_canonical update(value: Int) {
  shadow { drink x: Int = value; }
  invariant { drink check: Bool = value > 0; }
  canonical { canonical_value = value; }
}
"""
        module = parse_shadow(src)
        self.assertEqual(len(module.module_invariants), 1)
        inv = module.module_invariants[0]
        self.assertEqual(inv.name, "positive")
        self.assertEqual(inv.params, [("n", "Int")])
        self.assertEqual(len(module.mutations), 1)

    def test_multiple_module_invariants(self):
        src = """
invariant positive(n: Int) { drink check: Bool = n > 0; }
invariant non_empty(s: String) { drink check: Bool = length(s) > 0; }

mutation validated_canonical safe(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = val > 0; }
  canonical { canonical_val = val; }
}
"""
        module = parse_shadow(src)
        self.assertEqual(len(module.module_invariants), 2)
        names = {inv.name for inv in module.module_invariants}
        self.assertIn("positive", names)
        self.assertIn("non_empty", names)


# ── Language: atomic groups ───────────────────────────────────────────────────

class TestAtomicGroups(unittest.TestCase):

    def test_atomic_group_parsed(self):
        src = """
atomic ledger_update {
  mutation validated_canonical debit(amount: Int) {
    shadow { drink x: Int = amount; }
    invariant { drink ok: Bool = amount > 0; }
    canonical { canonical_debit = amount; }
  }
  mutation validated_canonical credit(amount: Int) {
    shadow { drink x: Int = amount; }
    invariant { drink ok: Bool = amount > 0; }
    canonical { canonical_credit = amount; }
  }
}
"""
        module = parse_shadow(src)
        self.assertEqual(len(module.atomic_groups), 1)
        group = module.atomic_groups[0]
        self.assertEqual(group.name, "ledger_update")
        self.assertEqual(len(group.mutations), 2)
        names = {m.name for m in group.mutations}
        self.assertIn("debit", names)
        self.assertIn("credit", names)

    def test_atomic_promote_all_pass(self):
        src = """
atomic clean_group {
  mutation validated_canonical a(val: Int) {
    shadow { drink x: Int = val; }
    invariant { drink ok: Bool = val > 0; }
    canonical { canonical_a = val; }
  }
  mutation validated_canonical b(val: Int) {
    shadow { drink y: Int = val; }
    invariant { drink ok: Bool = val > 0; }
    canonical { canonical_b = val; }
  }
}
"""
        module = parse_shadow(src)
        result = promote_atomic(module.atomic_groups[0])
        self.assertEqual(result["verdict"], "PROMOTE")

    def test_atomic_promote_one_fail_rejects_all(self):
        src = """
atomic mixed_group {
  mutation validated_canonical good(val: Int) {
    shadow { drink x: Int = val; }
    invariant { drink ok: Bool = val > 0; }
    canonical { canonical_good = val; }
  }
  mutation validated_canonical bad(val: Int) {
    shadow { drink t: Any = now(); }
    invariant { drink ok: Bool = parched; }
    canonical { canonical_bad = val; }
  }
}
"""
        module = parse_shadow(src)
        result = promote_atomic(module.atomic_groups[0])
        self.assertEqual(result["verdict"], "REJECT")


# ── Replay hash content-sensitivity ──────────────────────────────────────────

class TestReplayHash(unittest.TestCase):

    def test_hash_is_stable(self):
        src = """
mutation validated_canonical stable(n: Int) {
  shadow { drink x: Int = n; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_n = n; }
}
"""
        r1 = replay_hash(parse_shadow(src))
        r2 = replay_hash(parse_shadow(src))
        self.assertEqual(r1, r2)

    def test_different_content_same_count_produces_different_hash(self):
        """Core fix: same statement count but different content = different hash."""
        src_a = """
mutation validated_canonical m(n: Int) {
  shadow { drink x: Int = n; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_n = n; }
}
"""
        src_b = """
mutation validated_canonical m(n: Int) {
  shadow { drink x: Int = 42; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_n = n; }
}
"""
        self.assertNotEqual(replay_hash(parse_shadow(src_a)), replay_hash(parse_shadow(src_b)))

    def test_hash_is_sha256_length(self):
        src = """
mutation validated_canonical h(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        h = replay_hash(parse_shadow(src))
        self.assertEqual(len(h), 64)


# ── Full promote integration ──────────────────────────────────────────────────

class TestPromoteIntegration(unittest.TestCase):

    def test_clean_mutation_promotes(self):
        src = """
mutation validated_canonical set_counter(value: Int) {
  shadow { drink mut temp: Int = value; temp = temp + 1; }
  invariant { drink check: Bool = value > 0; }
  canonical { canonical_counter = value; }
}
"""
        result = promote(parse_shadow(src))
        self.assertEqual(result["verdict"], "PROMOTE")
        self.assertIn("replay_hash", result)
        self.assertEqual(len(result["replay_hash"]), 64)
        self.assertEqual(result["failures"], [])

    def test_dry_run_flag_propagated(self):
        src = """
mutation validated_canonical dry(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_val = val; }
}
"""
        result = promote(parse_shadow(src), dry_run=True)
        self.assertTrue(result["dry_run"])

    def test_result_has_all_eleven_analyzers(self):
        src = """
mutation validated_canonical full(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = val > 0; }
  canonical { canonical_val = val; }
}
"""
        results = analyze(parse_shadow(src))
        names = {r.analyzer for r in results}
        expected = {
            "PlaneIsolationAnalyzer",
            "DeterminismAnalyzer",
            "PuritySpringAnalyzer",
            "CanonicalConvergenceAnalyzer",
            "PrivilegeEscalationAnalyzer",
            "DeadShadowAnalyzer",
            "ResourceEstimator",
            "MemoryEvaporationAnalyzer",
            "DivergenceRiskAnalyzer",
            "SectionOrderAnalyzer",
            "InvariantCompletenessAnalyzer",
        }
        self.assertEqual(names, expected)

    def test_reject_result_includes_failure_list(self):
        src = """
mutation validated_canonical bad() {
  shadow { drink t: Any = now(); }
  invariant { drink ok: Bool = parched; }
  canonical { canonical_t = 0; }
}
"""
        result = promote(parse_shadow(src))
        self.assertEqual(result["verdict"], "REJECT")
        self.assertIn("DeterminismAnalyzer", result["failures"])

    def test_mutation_name_on_each_result(self):
        src = """
mutation validated_canonical named(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = val > 0; }
  canonical { canonical_val = val; }
}
"""
        results = analyze(parse_shadow(src))
        for r in results:
            self.assertEqual(r.mutation, "named")

    def test_visualize_includes_on_reject_edge(self):
        src = """
mutation validated_canonical with_handler(val: Int) {
  shadow { drink x: Int = val; }
  invariant { drink ok: Bool = val > 0; }
  canonical { canonical_val = val; }
  on_reject { pour("withheld"); }
}
"""
        diagram = visualize(parse_shadow(src))
        self.assertIn("on_reject", diagram)
        self.assertIn("reject", diagram)


if __name__ == "__main__":
    unittest.main()
