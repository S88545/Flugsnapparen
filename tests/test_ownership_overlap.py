import pytest

@pytest.mark.skip(reason="Integration test requires app + DB seed; enable when test DB is configured.")
def test_ownership_date_overlap_blocked():
    """
    Scenario: Existing ownership A: [2024-01-01 .. 2024-12-31]
    When editing ownership B to overlap with A
    Expectation: Server responds with validation message (e.g., 200 with flash 'Datum överlappar ...') and does not commit.
    Steps to implement when enabling:
    - Seed apartment, member(s), ownership A
    - POST /apartments/ownerships/edit/<idB> with overlapping dates
    - Assert flash message and unchanged DB state
    """
    assert True
