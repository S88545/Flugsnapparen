import pytest

@pytest.mark.skip(reason="Integration test requires app + DB seed; enable when test DB is configured.")
def test_transactions_filtered_by_period_year():
    """
    Scenario: Two transactions with different transaction_date years but same period_year
    Expectation: Listing/report endpoints for selected year include both when filtering by period_year.
    Steps to implement when enabling:
    - Create transaction t1: date=2024-12-30, period_year=2025
    - Create transaction t2: date=2025-01-02, period_year=2025
    - GET /transactions?year=2025&year_mode=period -> both present
    - Reports summary for 2025 reflect sum(t1.amount + t2.amount)
    """
    assert True
