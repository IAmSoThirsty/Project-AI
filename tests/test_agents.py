from app.core.ai_persona import AIPersona


def test_agents_instantiation_and_basic_calls(tmp_path):
    # Use an isolated data directory for the persona
    data_dir = str(tmp_path / "persona_data")
    p = AIPersona(data_dir=data_dir)

    # Oversight: harmless action should be allowed
    allowed, reason = p.oversight_evaluate("Compute a report", {})
    assert isinstance(allowed, bool)
    assert isinstance(reason, str)

    # Oversight: harmful action should be denied
    allowed2, reason2 = p.oversight_evaluate("We should exterminate X", {})
    assert allowed2 is False

    # Validator: non-empty string passes
    ok, vreason = p.validate_item("Do something", {})
    assert ok is True

    # Retrieval: without memory system should return empty list
    results = p.retrieve_knowledge("any query")
    assert isinstance(results, list)

    # Planner: plan should be a list of steps
    plan = p.create_plan("Organize files")
    assert isinstance(plan, list)
    assert len(plan) >= 1

    # Explainability: should return a dict (likely empty on fresh persona)
    expl = p.explain_model("zeroth", top_n=3)
    assert isinstance(expl, dict)

    # Executor: simulate executing plan
    plan = ["Step 1: prepare", "Step 2: execute"]
    res = p.execute_plan(plan, dry_run=True)
    assert isinstance(res, list)

    # Learner: curate (empty dir returns empty dict)
    counts = p.curate_dataset(str(tmp_path / "no_data"))
    assert isinstance(counts, dict)

    # Privacy: detect/no detect
    pii = p.find_pii("Contact me at test@example.com or +1 555 123 4567")
    assert isinstance(pii, list)

    # Metrics: record and query
    p.record_metric("test.metric", 1.23, tags={"k": "v"})
    metrics = p.query_metric("test.metric")
    assert isinstance(metrics, list)

    # Web harvester: request queued
    req = p.request_harvest("https://example.com", depth=1)
    # may be None if agent unavailable, otherwise dict
    assert (req is None) or isinstance(req, dict)

    # Personalization: update/get
    upd = p.personalize({"theme": "dark"})
    assert isinstance(upd, dict)

    # Audit: record explainability (will return False if audit agent missing)
    ae = p.audit_explain("zeroth", [{"token": "test", "weight": 1.0}], meta={})
    assert isinstance(ae, bool)
