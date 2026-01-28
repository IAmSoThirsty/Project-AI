def export_audit():
    with open(__file__.replace("audit_export.py","governance_audit.log")) as f:
        return f.read().splitlines()
