import unittest

from shadow_thirst.core import analyze, parse_shadow, promote


class ShadowTests(unittest.TestCase):
    def test_analyze(self):
        text = """
mutation validated_canonical m(value: Int) {
  shadow {
    drink mut x: Int = value;
    x = x + 1;
  }
  invariant {
    length("ok");
  }
  canonical {
    canonical_counter = value;
  }
}
"""
        module = parse_shadow(text)
        results = analyze(module)
        self.assertTrue(any(r.name == "PlaneIsolationAnalyzer" for r in results))
        verdict = promote(module)["verdict"]
        self.assertEqual(verdict, "PROMOTE")

    def test_reject_nondeterminism(self):
        text = """
mutation validated_canonical m(value: Int) {
  shadow {
    now();
  }
  invariant {
    length("ok");
  }
  canonical {
    canonical_counter = value;
  }
}
"""
        module = parse_shadow(text)
        verdict = promote(module)["verdict"]
        self.assertEqual(verdict, "REJECT")


if __name__ == "__main__":
    unittest.main()
