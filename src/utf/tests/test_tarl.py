import unittest
import sys
from pathlib import Path

UTF_SRC = Path(__file__).resolve().parent.parent
while str(UTF_SRC) in sys.path:
    sys.path.remove(str(UTF_SRC))
sys.path.insert(0, str(UTF_SRC))
for module_name in list(sys.modules):
    if module_name == "tarl" or module_name.startswith("tarl."):
        sys.modules.pop(module_name, None)

from tarl.core import evaluate, parse_policy


class TarlTests(unittest.TestCase):
    def test_eval(self):
        policy = parse_policy("""
policy P {
  when actor.role == "builder" => ALLOW;
  when mutation.risk > 3 => ESCALATE;
}
""")
        self.assertEqual(
            evaluate(policy, {"actor": {"role": "builder"}, "mutation": {"risk": 1}}),
            "ALLOW",
        )
        self.assertEqual(
            evaluate(policy, {"actor": {"role": "x"}, "mutation": {"risk": 5}}),
            "ESCALATE",
        )
        self.assertEqual(
            evaluate(policy, {"actor": {"role": "x"}, "mutation": {"risk": 1}}), "DENY"
        )


if __name__ == "__main__":
    unittest.main()
