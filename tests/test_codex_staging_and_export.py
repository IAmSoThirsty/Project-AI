import hashlib
import json
import os

from app.agents.codex_deus_maximus import create_codex
from app.core.access_control import get_access_control


def test_integrate_approved_creates_backup_and_import(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    codex = create_codex(data_dir=str(data_dir), allow_integration=True)
    # prepare generated dir and a fake generated module
    gen_dir = tmp_path / "generated"
    gen_dir.mkdir()
    codex.generated_dir = str(gen_dir)
    module_path = gen_dir / "impl_test.py"
    module_path.write_text("def impl_test():\n    return True\n")

    # prepare target file
    target = tmp_path / "target_module.py"
    target.write_text("# target module\n")

    res = codex.integrate_approved(target_modules=[str(target)])
    assert res.get("success")
    # backup exists
    bak = str(target) + ".codexbak"
    assert os.path.exists(bak)
    # import line appended
    content = target.read_text()
    assert "from app.generated import impl_test" in content


def test_stage_and_activate_staged_requires_integrator(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    codex = create_codex(data_dir=str(data_dir), allow_integration=True)
    # create archived artifact
    gen_dir = tmp_path / "generated"
    gen_dir.mkdir()
    codex.generated_dir = str(gen_dir)
    archived = gen_dir / "archived_impl.py"
    archived.write_text("def archived_impl():\n    return True\n")

    # stage artifact
    staged = codex.stage_artifact("req1", str(archived), "topic1", "desc")
    assert staged.get("success")
    staged_path = staged["staged"]

    # without integrator role activation should fail
    ac = get_access_control()
    if ac.has_role("system", "integrator"):
        ac.revoke_role("system", "integrator")
    res = codex.activate_staged(staged_path, requester="system")
    assert not res.get("success")

    # grant integrator and try again
    ac.grant_role("system", "integrator")
    res2 = codex.activate_staged(staged_path, requester="system")
    # integration may succeed (no targets present) but should return a dict
    assert isinstance(res2, dict)


def test_export_audit_creates_signed_file(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    codex = create_codex(data_dir=str(data_dir), allow_integration=False)
    # write a dummy audit
    audit_path = os.path.join(str(data_dir), "codex_audit.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump([{"ts": "now", "action": "test"}], f)
    codex.audit_path = audit_path

    ac = get_access_control()
    ac.grant_role("tester", "expert")
    res = codex.export_audit(requester="tester")
    assert res.get("success")
    out = res.get("out")
    sig = res.get("signature")
    sig_path = res.get("signature_path")
    assert os.path.exists(out)
    assert sig is not None
    assert os.path.exists(sig_path)
    # verify signature matches file
    with open(out, "rb") as f:
        data = f.read()
    assert hashlib.sha256(data).hexdigest() == sig
