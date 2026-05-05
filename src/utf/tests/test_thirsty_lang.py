import unittest

from thirsty_lang.cli import check_source, run_source


class ThirstyLangTests(unittest.TestCase):
    def test_hello(self):
        src = """
glass main() -> Int {
  pour("hello");
  return 0;
}
"""
        self.assertEqual(run_source(src), ["hello"])

    def test_if_loop_function_array(self):
        src = """
glass add(a: Int, b: Int) -> Int {
  return a + b;
}
glass main() -> Int {
  drink mut items: Reservoir[Int] = [1, 2, 3];
  thirsty (size(items) == 3) {
    refill 2 times {
      pour(add(1, 2));
    }
  } hydrated {
    pour("bad");
  }
  return 0;
}
"""
        self.assertEqual(run_source(src), ["3", "3"])

    def test_gods_class_async_try(self):
        src = """
fountain Counter {
  drink mut value: Int;
  glass init(start: Int) {
    this.value = start;
  }
  glass inc() -> Int {
    this.value = this.value + 1;
    return this.value;
  }
  cascade glass current() -> Int {
    return this.value;
  }
}
glass main() -> Int {
  drink mut c: Counter = new Counter(1);
  pour(c.inc());
  pour(await c.current());
  spillage {
    throw "boom";
  } cleanup error (e: Error) {
    pour(e);
  }
  return 0;
}
"""
        self.assertEqual(run_source(src), ["2", "2", "boom"])

    def test_check(self):
        src = """
glass main() -> Int {
  drink x: Int = 1;
  return x;
}
"""
        check_source(src)


if __name__ == "__main__":
    unittest.main()
