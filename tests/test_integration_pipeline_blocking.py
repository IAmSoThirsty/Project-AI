from app.agents.codex_deus_maximus import create_codex
from app.core.council_hub import CouncilHub


def test_integration_blocked_on_qa(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    codex = create_codex(data_dir=str(data_dir), allow_integration=True)
    # setup hub and project to include QA that will fail
    hub = CouncilHub()
    hub.register_project("TestProject")
    # create generated file
    gen_dir = tmp_path / "generated"
    gen_dir.mkdir()
    codex.generated_dir = str(gen_dir)
    bad = gen_dir / "bad_impl.py"
    bad.write_text("def bad_impl():\n    raise Exception('fail')\n")
    # ensure project agents point to this generated_dir via codex
    hub._project["qa_generator"] = hub._project["qa_generator"]
    hub._project["dependency_auditor"] = hub._project["dependency_auditor"]
    # call integrate_approved which should run QA and fail
    res = codex.integrate_approved(target_modules=[str(tmp_path / "target.py")])
    assert not res.get("success") and res.get("blocked")
