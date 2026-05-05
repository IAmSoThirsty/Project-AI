import unittest

from thirsty_lang.cli import check_source, run_source


class ThirstyFlavorTests(unittest.TestCase):
    def test_drip_pipe_guard_and_well(self):
        src = """
glass inc(x: Int) -> Int {
  return x + 1;
}
glass double(x: Int) -> Int {
  return x * 2;
}
glass main() -> Int {
  drink mut counter: Int = 1;
  drip counter += 2;
  drink bucket: well[of: Int] = [1, 2, 3];
  pour(counter);
  pour(3 |> inc |> double);
  pour(thirst counter > 1 quench "hydrated" hydrated "dry");
  pour(bucket.size());
  return 0;
}
"""
        self.assertEqual(run_source(src), ["3", "8", "hydrated", "3"])

    def test_safe_input_and_option_condense(self):
        src = """
glass main() -> Int {
  drink maybe: Quenched[String] = sip?();
  thirsty (maybe != empty) {
    pour(condense maybe);
  } hydrated {
    pour("empty");
  }
  return 0;
}
"""
        self.assertEqual(run_source(src), ["empty"])

    def test_reservoir_methods(self):
        src = """
glass keep_even(x: Int) -> Bool {
  return x % 2 == 0;
}
glass plus_one(x: Int) -> Int {
  return x + 1;
}
glass sum(acc: Int, x: Int) -> Int {
  return acc + x;
}
glass main() -> Int {
  drink nums: Reservoir[Int] = [1, 2, 3, 4];
  drink evens: Reservoir[Any] = nums.strain(keep_even);
  drink mapped: Reservoir[Any] = evens.transmute(plus_one);
  pour(size(evens));
  pour(mapped.distill(0, sum));
  return 0;
}
"""
        self.assertEqual(run_source(src), ["2", "8"])

    def test_finally_runs(self):
        src = """
glass main() -> Int {
  spillage {
    throw "boom";
  } cleanup error (e: Error) {
    pour(e);
  } cleanup finally {
    pour("always");
  }
  return 0;
}
"""
        self.assertEqual(run_source(src), ["boom", "always"])

    def test_did_you_mean(self):
        bad = """
glass main() -> Int {
  drink x: Int = 1;
  thirsty (parchedd) {
    pour(x);
  }
  return 0;
}
"""
        with self.assertRaises(Exception) as ctx:
            check_source(bad)
        self.assertIn("parched", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
