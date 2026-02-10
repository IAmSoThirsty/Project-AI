import importlib
import sys
from pathlib import Path

# Add src to path so imports work
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

modules = [
    "app.core.user_manager",
    "app.core.location_tracker",
    "app.core.emergency_alert",
    "app.core.learning_paths",
    "app.core.data_analysis",
    "app.core.security_resources",
]
for m in modules:
    try:
        importlib.import_module(m)
        print(f"OK: {m}")
    except Exception as e:
        print(f"ERR: {m} -> {e}")
