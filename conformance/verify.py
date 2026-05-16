"""Lightweight in-process conformance verifier for Phase 2.
Runs tests by importing the interpreter directly — no subprocess overhead.
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'utf'))

from thirsty_lang.cli import run_source, check_source
from thirsty_lang.diagnostics import ThirstyError, DiagnosticBundle

PASS = "PASS"
FAIL = "FAIL"
results = []

def test(description: str, source: str, expected_stdout: str, expect_error: bool = False, error_code: str = ""):
    try:
        out = run_source(source, "<test>")
        actual = "\n".join(str(x) for x in out) + ("\n" if out else "")
        if expect_error:
            results.append((FAIL, description, f"expected error but got: {actual!r}"))
        elif actual == expected_stdout:
            results.append((PASS, description, ""))
        else:
            results.append((FAIL, description, f"expected {expected_stdout!r} got {actual!r}"))
    except (ThirstyError, DiagnosticBundle, Exception) as e:
        msg = str(e)
        if expect_error:
            if error_code and error_code not in msg:
                results.append((FAIL, description, f"wrong error code in: {msg[:80]}"))
            else:
                results.append((PASS, description, ""))
        else:
            results.append((FAIL, description, f"unexpected error: {msg[:120]}"))

# ── Syntax ───────────────────────────────────────────────────────────────────
test("hello world", 'glass main() -> Int { pour("hello"); return 0; }', "hello\n")
test("integer literal", 'glass main() -> Int { pour(42); return 0; }', "42\n")
test("arithmetic", 'glass main() -> Int { pour(3 + 4 * 2); return 0; }', "11\n")
test("thirsty/hydrated", 'glass main() -> Int { thirsty (parched) { pour("yes"); } hydrated { pour("no"); } return 0; }', "yes\n")
test("refill loop", 'glass main() -> Int { drink mut i: Int = 0; refill 3 times { drip i; } pour(i); return 0; }', "3\n")
test("function call", 'glass add(a: Int, b: Int) -> Int { return a + b; } glass main() -> Int { pour(add(3,4)); return 0; }', "7\n")
test("recursion factorial", 'glass fact(n: Int) -> Int { thirsty (n <= 1) { return 1; } return n * fact(n-1); } glass main() -> Int { pour(fact(5)); return 0; }', "120\n")
test("pipe operator", 'glass dbl(x: Int) -> Int { return x * 2; } glass main() -> Int { pour(5 |> dbl); return 0; }', "10\n")
test("module header core", 'module app\nmode core\nglass main() -> Int { pour("ok"); return 0; }', "ok\n")
test("module header governed", 'module app\nmode governed\nglass main() -> Int { pour("gov"); return 0; }', "gov\n")

# ── Type errors ──────────────────────────────────────────────────────────────
test("duplicate binding", 'glass main() -> Int { drink x: Int = 1; drink x: Int = 2; return 0; }', "", expect_error=True, error_code="THIRSTY-E010")
test("unknown identifier", 'glass main() -> Int { pour(zz); return 0; }', "", expect_error=True, error_code="THIRSTY-E011")
test("immutable assign", 'glass main() -> Int { drink x: Int = 1; x = 2; return 0; }', "", expect_error=True, error_code="THIRSTY-E020")
test("arity mismatch", 'glass f(a: Int) -> Int { return a; } glass main() -> Int { f(1,2); return 0; }', "", expect_error=True, error_code="THIRSTY-E030")

# ── Error handling ───────────────────────────────────────────────────────────
test("spillage catches", 'glass main() -> Int { spillage { throw "x"; } cleanup (e: Error) { pour("caught"); } return 0; }', "caught\n")
test("finally always runs", 'glass main() -> Int { spillage { pour("try"); } cleanup (e: Error) { pour("c"); } finally { pour("fin"); } return 0; }', "try\nfin\n")
test("div by zero E101", 'glass main() -> Int { drink x: Int = 1 / 0; return 0; }', "", expect_error=True, error_code="THIRSTY-E101")
test("condense empty E901", 'glass main() -> Int { drink v: Any = empty; condense(v); return 0; }', "", expect_error=True, error_code="THIRSTY-E901")

# ── Stdlib builtins ──────────────────────────────────────────────────────────
test("length builtin", 'glass main() -> Int { pour(length("hello")); return 0; }', "5\n")
test("contains True", 'glass main() -> Int { pour(contains("hello world", "world")); return 0; }', "True\n")
test("contains False", 'glass main() -> Int { pour(contains("hello", "xyz")); return 0; }', "False\n")
test("split builtin", 'glass main() -> Int { drink p: Reservoir[String] = split("a,b,c", ","); pour(size(p)); return 0; }', "3\n")
test("abs builtin", 'glass main() -> Int { pour(abs(-7)); return 0; }', "7\n")
test("min builtin", 'glass main() -> Int { pour(min(3,7)); return 0; }', "3\n")
test("max builtin", 'glass main() -> Int { pour(max(3,7)); return 0; }', "7\n")
test("push/size", 'glass main() -> Int { drink mut xs: Reservoir[Int] = []; push(xs,1); push(xs,2); pour(size(xs)); return 0; }', "2\n")
test("get builtin", 'glass main() -> Int { drink xs: Reservoir[Int] = [10,20,30]; pour(get(xs,1)); return 0; }', "20\n")
test("strain builtin", 'glass main() -> Int { drink xs: Reservoir[Int] = [1,2,3,4]; drink e: Reservoir[Int] = strain(xs, glass(x: Int) -> Bool { return x % 2 == 0; }); pour(size(e)); return 0; }', "2\n")
test("transmute builtin", 'glass main() -> Int { drink xs: Reservoir[Int] = [1,2,3]; drink d: Reservoir[Int] = transmute(xs, glass(x: Int) -> Int { return x*2; }); pour(get(d,0)); return 0; }', "2\n")
test("distill builtin", 'glass main() -> Int { drink xs: Reservoir[Int] = [1,2,3,4]; drink s: Int = distill(xs, 0, glass(a: Int, x: Int) -> Int { return a+x; }); pour(s); return 0; }', "10\n")

# ── Module stdlib namespaces ─────────────────────────────────────────────────
test("thirst::crypto sha256", 'import thirst::crypto\nglass main() -> Int { drink h: String = thirst::crypto.sha256("x"); pour(length(h) == 64); return 0; }', "True\n")
test("thirst::crypto sign", 'import thirst::crypto\nglass main() -> Int { drink s: String = thirst::crypto.sign("x"); pour(contains(s, "signed:")); return 0; }', "True\n")
test("thirst::crypto uuid4", 'import thirst::crypto\nglass main() -> Int { drink u: String = thirst::crypto.uuid4(); pour(length(u) == 36); return 0; }', "True\n")
test("thirst::time now", 'import thirst::time\nglass main() -> Int { drink t: Int = thirst::time.now(); pour(t > 0); return 0; }', "True\n")
test("thirst::fs exists dot", 'import thirst::fs\nglass main() -> Int { pour(thirst::fs.exists(".")); return 0; }', "True\n")
test("thirst::fs exists false", 'import thirst::fs\nglass main() -> Int { pour(thirst::fs.exists("/no/such/path/xyz99")); return 0; }', "False\n")
test("thirst::json stringify", 'import thirst::json\nglass main() -> Int { drink s: String = thirst::json.stringify(42); pour(s); return 0; }', "42\n")
test("thirst::env get PATH", 'import thirst::env\nglass main() -> Int { drink v: Any = thirst::env.get("PATH"); pour(v != empty); return 0; }', "True\n")
test("thirst::collections sort", 'import thirst::collections\nglass main() -> Int { drink xs: Reservoir[Int] = [3,1,2]; drink ys: Any = thirst::collections.sort(xs); pour(get(ys,0)); return 0; }', "1\n")
test("thirst::collections unique", 'import thirst::collections\nglass main() -> Int { drink xs: Reservoir[Int] = [1,2,2,3]; drink ys: Any = thirst::collections.unique(xs); pour(size(ys)); return 0; }', "3\n")
test("thirst::path basename", 'import thirst::path\nglass main() -> Int { pour(thirst::path.basename("/foo/bar.txt")); return 0; }', "bar.txt\n")
test("thirst::path extension", 'import thirst::path\nglass main() -> Int { pour(thirst::path.extension("hello.thirsty")); return 0; }', ".thirsty\n")
test("thirst::process pid", 'import thirst::process\nglass main() -> Int { drink p: Any = thirst::process.pid(); pour(p > 0); return 0; }', "True\n")

# ── Security keywords ────────────────────────────────────────────────────────
test("shield executes", 'glass main() -> Int { shield { pour("ok"); } return 0; }', "ok\n")
test("sanitize passthrough", 'glass main() -> Int { drink v: Any = sanitize("x"); pour(v); return 0; }', "x\n")
test("armor passthrough", 'glass main() -> Int { drink v: Any = armor(1); pour(v); return 0; }', "1\n")
test("defend true passes", 'glass main() -> Int { defend(parched); pour("safe"); return 0; }', "safe\n")
test("defend false halts", 'glass main() -> Int { defend(quenched); pour("never"); return 0; }', "", expect_error=True)

# ── Classes ──────────────────────────────────────────────────────────────────
test("class method", 'fountain Ctr { drink mut n: Int = 0; glass inc() -> Void { drip n; } glass val() -> Int { return n; } } glass main() -> Int { drink c: Any = new Ctr(); c.inc(); c.inc(); pour(c.val()); return 0; }', "2\n")

# ── Advanced ─────────────────────────────────────────────────────────────────
test("closure over arg", 'glass adder(n: Int) -> Any { return glass(x: Int) -> Int { return x + n; }; } glass main() -> Int { drink f: Any = adder(5); pour(f(10)); return 0; }', "15\n")
test("chained pipes", 'glass inc(x: Int) -> Int { return x+1; } glass dbl(x: Int) -> Int { return x*2; } glass main() -> Int { pour(3 |> inc |> dbl); return 0; }', "8\n")
test("tail recursion sum 100", 'glass s(n: Int, a: Int) -> Int { thirsty (n <= 0) { return a; } return s(n-1, a+n); } glass main() -> Int { pour(s(100,0)); return 0; }', "5050\n")

# ── Results ──────────────────────────────────────────────────────────────────
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
print(f"\n{'─'*50}")
for status, desc, detail in results:
    if status == FAIL:
        print(f"  FAIL  {desc}")
        print(f"        {detail}")
print(f"\nResults: {passed}/{passed+failed} passed")
if failed:
    sys.exit(1)
