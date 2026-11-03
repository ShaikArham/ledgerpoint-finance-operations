from datetime import date
import pytest
from ledgerpoint.cases import create_case, update_case

def test_case_creation_and_resolution():
    case = create_case("CASE-001", "UNKNOWN-001", "bank_only")
    assert case.status == "Open"
    case = update_case(case, status="Investigating", priority="High",
                       owner="Demo analyst", note="Review statement", event_date=date(2026,10,31))
    assert len(case.history) == 1
    assert case.priority == "High"
    case = update_case(case, status="Resolved", priority="High", owner="Demo analyst",
                       note="Reviewed supporting documents", resolution="Verified bank fee",
                       event_date=date(2026,11,1))
    assert case.status == "Resolved"
    assert len(case.history) == 2
    assert case.resolution == "Verified bank fee"

def test_resolution_requires_explanation():
    case = create_case("CASE-001", "UNKNOWN-001", "bank_only")
    with pytest.raises(ValueError, match="resolution"):
        update_case(case, status="Resolved", priority="Medium", owner="Analyst", note="Done")

def test_no_blank_owner_or_note():
    case = create_case("CASE-001", "UNKNOWN-001", "bank_only")
    with pytest.raises(ValueError, match="owner"):
        update_case(case, status="Investigating", priority="Medium", owner="", note="Review")
    with pytest.raises(ValueError, match="note"):
        update_case(case, status="Investigating", priority="Medium", owner="Analyst", note="")

def test_resolved_case_cannot_reopen():
    case = create_case("CASE-001", "UNKNOWN-001", "bank_only")
    case = update_case(case, status="Resolved", priority="Low", owner="Analyst",
                       note="Evidence checked", resolution="No adjustment required")
    with pytest.raises(ValueError, match="cannot be reopened"):
        update_case(case, status="Open", priority="Low", owner="Analyst", note="Reopen")

def test_case_update_does_not_change_original():
    original = create_case("CASE-001", "UNKNOWN-001", "bank_only")
    updated = update_case(original, status="Investigating", priority="Medium",
                          owner="Analyst", note="Review")
    assert original.status == "Open"
    assert original.history == ()
    assert updated.history
