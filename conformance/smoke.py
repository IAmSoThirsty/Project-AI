import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'utf'))
from thirsty_lang.cli import run_source

# Import syntax: import "thirst::module" as alias;   (semicolon required)
# Access syntax: alias.function(...)

tests = [
    ("hello world",
     'glass main() -> Int { pour("hello"); return 0; }',
     ["hello"]),
    ("arithmetic",
     'glass main() -> Int { pour(3+4); return 0; }',
     ["7"]),
    ("module header core",
     'module app\nmode core\nglass main() -> Int { pour("ok"); return 0; }',
     ["ok"]),
    ("module header governed",
     'module app\nmode governed\nglass main() -> Int { pour("gov"); return 0; }',
     ["gov"]),
    ("crypto sha256",
     'import "thirst::crypto" as crypto;\nglass main() -> Int { drink h: String = crypto.sha256("x"); pour(length(h) == 64); return 0; }',
     ["True"]),
    ("crypto sign",
     'import "thirst::crypto" as crypto;\nglass main() -> Int { pour(contains(crypto.sign("x"), "signed:")); return 0; }',
     ["True"]),
    ("crypto uuid4",
     'import "thirst::crypto" as crypto;\nglass main() -> Int { drink u: String = crypto.uuid4(); pour(length(u) == 36); return 0; }',
     ["True"]),
    ("crypto hmac",
     'import "thirst::crypto" as crypto;\nglass main() -> Int { drink h: String = crypto.hmac("key", "msg"); pour(length(h) > 0); return 0; }',
     ["True"]),
    ("fs exists true",
     'import "thirst::fs" as fs;\nglass main() -> Int { pour(fs.exists(".")); return 0; }',
     ["True"]),
    ("fs exists false",
     'import "thirst::fs" as fs;\nglass main() -> Int { pour(fs.exists("/no/such/path/xyz99999")); return 0; }',
     ["False"]),
    ("collections sort",
     'import "thirst::collections" as col;\nglass main() -> Int { drink xs: Reservoir[Int] = [3,1,2]; drink ys: Any = col.sort(xs); pour(get(ys,0)); return 0; }',
     ["1"]),
    ("collections unique",
     'import "thirst::collections" as col;\nglass main() -> Int { drink xs: Reservoir[Int] = [1,2,2,3]; drink ys: Any = col.unique(xs); pour(size(ys)); return 0; }',
     ["3"]),
    ("collections filter",
     'import "thirst::collections" as col;\nglass main() -> Int { drink xs: Reservoir[Int] = [1,2,3,4]; drink ys: Any = col.filter(xs, glass(x: Int) -> Bool { return x % 2 == 0; }); pour(size(ys)); return 0; }',
     ["2"]),
    ("json stringify",
     'import "thirst::json" as json;\nglass main() -> Int { pour(json.stringify(42)); return 0; }',
     ["42"]),
    ("json parse get",
     'import "thirst::json" as json;\nglass main() -> Int { drink obj: Any = json.parse("{\\\"x\\\": 99}"); pour(json.get(obj, "x")); return 0; }',
     ["99"]),
    ("path basename",
     'import "thirst::path" as p;\nglass main() -> Int { pour(p.basename("/foo/bar.txt")); return 0; }',
     ["bar.txt"]),
    ("path extension",
     'import "thirst::path" as p;\nglass main() -> Int { pour(p.extension("main.thirsty")); return 0; }',
     [".thirsty"]),
    ("env get PATH",
     'import "thirst::env" as env;\nglass main() -> Int { drink v: Any = env.get("PATH"); pour(v != empty); return 0; }',
     ["True"]),
    ("process pid",
     'import "thirst::process" as proc;\nglass main() -> Int { drink p: Any = proc.pid(); pour(p > 0); return 0; }',
     ["True"]),
    ("time now",
     'import "thirst::time" as t;\nglass main() -> Int { drink n: Int = t.now(); pour(n > 0); return 0; }',
     ["True"]),
    ("time format",
     'import "thirst::time" as t;\nglass main() -> Int { drink s: String = t.format(0, "%Y"); pour(length(s) > 0); return 0; }',
     ["True"]),
]

passed = failed = 0
for name, src, expected in tests:
    try:
        out = [str(x) for x in run_source(src, "<t>")]
        if out == expected:
            print(f"PASS  {name}")
            passed += 1
        else:
            print(f"FAIL  {name}  expected={expected!r} got={out!r}")
            failed += 1
    except Exception as e:
        print(f"FAIL  {name}  error={str(e)[:100]}")
        failed += 1

print(f"\n{passed}/{passed+failed} passed")
sys.exit(0 if failed == 0 else 1)
