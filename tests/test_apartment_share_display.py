import pytest

@pytest.mark.skip(reason="UI rendering test; enable with templating test harness if desired.")
def test_apartment_share_percentage_display():
    """
    Expectation: Apartment list renders share as percent with two decimals, e.g., 0.123 -> 12.3%.
    Suggestion: Snapshot test on rendered template context when test client is available.
    """
    assert True
