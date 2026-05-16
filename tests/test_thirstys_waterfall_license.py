from pathlib import Path

import thirstys_waterfall


def test_vendored_waterfall_declares_apache_2_license():
    assert thirstys_waterfall.__license__ == "Apache-2.0"


def test_vendored_waterfall_includes_apache_license_text():
    license_text = (
        Path(thirstys_waterfall.__file__).with_name("LICENSE").read_text(encoding="utf-8")
    )

    assert "Apache License" in license_text
    assert "Version 2.0, January 2004" in license_text
