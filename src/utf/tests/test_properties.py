
import random
import unittest

from shadow_thirst.core import analyze, parse_shadow
from thirsty_lang.cli import run_source
from tscg.core import canonical, parse, validate
from tscg_b.core import pack_text, unpack_frame


class PropertyStyleTests(unittest.TestCase):
    def test_tail_call_optimization_survives_deep_self_recursion(self):
        src = """
glass loop(n: Int, acc: Int) -> Int {
  thirsty (n == 0) {
    return acc;
  } hydrated {
    return loop(n - 1, acc + 1);
  }
}
glass main() -> Int {
  pour(loop(700, 0));
  return 0;
}
"""
        self.assertEqual(run_source(src), ["700"])

    def test_builtin_namespace_modules_import_and_run(self):
        src = """
import "thirst::crypto" as crypto;
import "thirst::time" as time;
glass main() -> Int {
  pour(crypto.sha256("water"));
  drink t: Int = time.now();
  pour(t);
  return 0;
}
"""
        out = run_source(src, "examples/namespace_imports.thirsty")
        self.assertEqual(len(out[0]), 64)
        self.assertTrue(out[1].isdigit())

    def test_tscg_and_tscgb_roundtrip_properties(self):
        symbols = ["COG", "DNT", "SHD(v1)", "INV", "CAP", "QRM", "COM", "ANC", "RFX"]
        rng = random.Random(1337)
        for _ in range(50):
            sample = " -> ".join(rng.choice(symbols) for _ in range(rng.randint(2, 6)))
            expr = parse(sample)
            validate(expr)
            can = canonical(expr)
            frame = pack_text(can)
            unpacked = unpack_frame(frame)
            self.assertEqual(unpacked["text"], can)

    def test_shadow_determinism_property(self):
        bad = """
mutation validated_canonical drift(x: Int) {
  shadow {
    drink t: Int = now();
  }
  invariant {
    drink ok: Bool = parched;
  }
  canonical {
    drink result: Int = x;
  }
}
"""
        results = analyze(parse_shadow(bad, "bad.shadowthirst"))
        failing = [r for r in results if r.name == "DeterminismAnalyzer"]
        self.assertTrue(failing)
        self.assertFalse(failing[0].passed)
