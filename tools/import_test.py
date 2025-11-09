import importlib
modules = [
    'app.core.user_manager',
    'app.core.location_tracker',
    'app.core.emergency_alert',
    'app.core.learning_paths',
    'app.core.data_analysis',
    'app.core.security_resources'
]
for m in modules:
    try:
        importlib.import_module(m)
        print(f'OK: {m}')
    except Exception as e:
        print(f'ERR: {m} -> {e}')
