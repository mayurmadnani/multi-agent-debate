from debate_system.core.tools import calculate, get_current_info, web_search


def test_calculate_simple():
    assert "Result" in calculate("2 + 2")


def test_calculate_rejects_invalid():
    assert "Error" in calculate("import os")


def test_get_current_info_formats():
    date_str = get_current_info("date")
    assert len(date_str) == 10


def test_web_search_returns_list():
    results = web_search("philosophy")
    assert isinstance(results, list)
    assert len(results) >= 1
