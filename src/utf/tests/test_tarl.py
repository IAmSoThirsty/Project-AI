import unittest

from tarl.core import evaluate, parse_policy


class TarlTests(unittest.TestCase):
    def test_eval(self):
        policy = parse_policy("""
policy P {
  when actor.role == "builder" => ALLOW;
  when mutation.risk > 3 => ESCALATE;
}
""")
        self.assertEqual(evaluate(policy, {"actor": {"role": "builder"}, "mutation": {"risk": 1}}), "ALLOW")
        self.assertEqual(evaluate(policy, {"actor": {"role": "x"}, "mutation": {"risk": 5}}), "ESCALATE")
        self.assertEqual(evaluate(policy, {"actor": {"role": "x"}, "mutation": {"risk": 1}}), "DENY")


if __name__ == "__main__":
    unittest.main()
