# Universal Thirsty Family — top-level package.
# Bootstrap packages use bare imports (tscg, thirsty_lang, shadow_thirst, …)
# that resolve relative to src/utf/. Add this directory to sys.path so those
# imports work when utf is loaded as a sub-package of src/.
import sys
from pathlib import Path

_utf_root = str(Path(__file__).parent)
if _utf_root not in sys.path:
    sys.path.insert(0, _utf_root)
