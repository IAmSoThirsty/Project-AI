from app.core.waterfall_filter import WaterfallResult, get_waterfall_filter


def test_waterfall_filter_loads_vendored_engine_by_default():
    result = get_waterfall_filter().filter(
        {"url": "https://example.com", "payload": {"body": "hello"}}
    )

    assert isinstance(result, WaterfallResult)
    assert result.allowed is True
    assert result.context["waterfall"]["engine"] == "thirstys_waterfall"


def test_waterfall_filter_blocks_tracker_url_before_governance():
    result = get_waterfall_filter().filter({"url": "https://doubleclick.net/ad"})

    assert result.allowed is False
    assert result.reason == "waterfall-content-blocker"
    assert result.context["waterfall"]["allowed"] is False


def test_waterfall_filter_blocks_phishing_url_before_governance():
    result = get_waterfall_filter().filter(
        {"url": "https://secure-login-verify.com/session"}
    )

    assert result.allowed is False
    assert result.reason == "waterfall-anti-phishing"
