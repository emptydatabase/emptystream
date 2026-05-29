from emptystream.utils import _format_duration


def test_none():
    assert _format_duration(None) == ""


def test_zero():
    assert _format_duration(0) == ""


def test_seconds_only():
    assert _format_duration(59) == "0:59"


def test_minutes():
    assert _format_duration(61) == "1:01"


def test_hours():
    assert _format_duration(3661) == "1:01:01"
