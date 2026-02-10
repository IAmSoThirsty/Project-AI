import random

from tarl import TarlRuntime
from tarl.policies.default import DEFAULT_POLICIES


def random_context():
    return {
        "mutation": random.choice([True, False, None]),
        "mutation_allowed": random.choice([True, False, None]),
        "agent": random.choice(["a", "b", None]),
    }


def fuzz(iterations=1000):
    runtime = TarlRuntime(DEFAULT_POLICIES)
    for _ in range(iterations):
        runtime.evaluate(random_context())
    return True


if __name__ == "__main__":
    print("FUZZ:", "PASS" if fuzz() else "FAIL")
