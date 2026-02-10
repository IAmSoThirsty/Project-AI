from app.core.council_hub import CouncilHub


def test_curator_integration(tmp_path):
    hub = CouncilHub()
    hub.register_project("TestProject")
    # Create a fake report and run curator
    report = {"topic": "t1", "neutral_summary": "a summary", "facts": ["fact1"]}
    res = hub._project["curator"].curate([report])
    assert res.get("added") >= 0


def test_qa_and_dependency(tmp_path):
    hub = CouncilHub()
    hub.register_project("TestProject")
    # Create a fake generated module
    gen_dir = tmp_path / "generated"
    gen_dir.mkdir()
    module = gen_dir / "impl_sample.py"
    module.write_text("def impl_sample():\n    return True\n")
    codex = hub._project.get("qa_generator")
    dep = hub._project.get("dependency_auditor")
    # Generate test
    res = codex.generate_test_for_module(str(module))
    assert res.get("success")
    # Run dependency auditor
    res2 = dep.analyze_new_module(str(module))
    assert res2.get("success")
