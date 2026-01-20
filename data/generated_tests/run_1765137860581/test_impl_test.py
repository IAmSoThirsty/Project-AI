import importlib.util
import inspect

spec = importlib.util.spec_from_file_location(
    "impl_test",
    r"C:\Users\Jeremy\AppData\Local\Temp\pytest-of-Jeremy\pytest-224\test_integrate_approved_create0\generated\impl_test.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, "impl_test")
_fn = mod.impl_test
try:
    sig = inspect.signature(_fn)
    # count required params (no defaults)
    req = [
        p
        for p in sig.parameters.values()
        if p.default is inspect._empty
        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    if len(req) == 0:
        # call the function and assert it does not raise and returns a truthy value
        res = _fn()
        assert res or res is None or res == True
except Exception:
    raise
