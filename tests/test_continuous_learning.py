from app.core.continuous_learning import ContinuousLearningEngine


def test_continuous_learning_generates_report(tmp_path):
    engine = ContinuousLearningEngine(data_dir=str(tmp_path))
    content = (
        "Renewable energy budgets reduce emissions, create jobs, and stabilize local grids. "
        "Communities see cleaner air after investments."
    )
    report = engine.absorb_information("Renewable Energy", content)

    assert report.topic == "Renewable Energy"
    assert len(report.facts) >= 1
    assert report.usage_ideas
    assert "perspective" in report.neutral_summary.lower()

    reloaded = ContinuousLearningEngine(data_dir=str(tmp_path))
    assert len(reloaded.reports) == 1
    assert reloaded.reports[0].topic == "Renewable Energy"


def test_continuous_learning_highlights_controversy(tmp_path):
    engine = ContinuousLearningEngine(data_dir=str(tmp_path))
    content = (
        "The policy debate includes a controversy between rapid deployment and measured oversight. "
        "Proponents praise innovation, while critics warn about unchecked costs."
    )
    report = engine.absorb_information("Energy Policy", content)

    assert report.pros_cons["pros"]
    assert report.pros_cons["cons"]
    assert "pros" in report.neutral_summary.lower() or "cons" in report.neutral_summary.lower()
