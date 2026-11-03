from datetime import datetime, timezone
import pytest
from ledgerpoint.approvals import ApprovalRegister, request_approval, review_approval

AT = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)

def sample():
    return request_approval(ApprovalRegister(), request_id="APR-001",
                            reference="UNKNOWN-001", actor="Maker",
                            reason="Review unmatched bank fee", at=AT)

def test_request_and_independent_approval():
    requested = sample()
    approved = review_approval(requested, request_id="APR-001", actor="Checker",
                               decision="Approved", note="Evidence checked", at=AT)
    assert requested.requests[0].status == "Pending"
    assert approved.requests[0].status == "Approved"
    assert [x.action for x in approved.events] == ["Requested", "Approved"]
    assert [x.sequence for x in approved.events] == [1, 2]
    assert approved.events[0].occurred_at.endswith("+00:00")

def test_rejection():
    result = review_approval(sample(), request_id="APR-001", actor="Checker",
                             decision="Rejected", note="Missing receipt")
    assert result.requests[0].status == "Rejected"

def test_self_approval_blocked_case_insensitive():
    with pytest.raises(ValueError, match="own request"):
        review_approval(sample(), request_id="APR-001", actor="maker",
                        decision="Approved", note="Looks fine")

def test_double_review_blocked():
    reviewed = review_approval(sample(), request_id="APR-001", actor="Checker",
                               decision="Approved", note="Checked")
    with pytest.raises(ValueError, match="already"):
        review_approval(reviewed, request_id="APR-001", actor="Other",
                        decision="Rejected", note="No")

def test_duplicate_request_blocked():
    with pytest.raises(ValueError, match="Duplicate"):
        request_approval(sample(), request_id="apr-001", reference="X",
                         actor="Maker", reason="Repeat")

@pytest.mark.parametrize("field", ["request_id", "reference", "actor", "reason"])
def test_required_request_fields(field):
    kwargs = dict(request_id="APR-002", reference="X", actor="Maker", reason="Review")
    kwargs[field] = " "
    with pytest.raises(ValueError, match="required"):
        request_approval(ApprovalRegister(), **kwargs)

def test_invalid_decision_and_unknown_request():
    with pytest.raises(ValueError, match="Decision"):
        review_approval(sample(), request_id="APR-001", actor="Checker",
                        decision="Pending", note="No")
    with pytest.raises(ValueError, match="not found"):
        review_approval(sample(), request_id="MISSING", actor="Checker",
                        decision="Approved", note="No")

def test_naive_timestamp_rejected():
    with pytest.raises(ValueError, match="timezone"):
        request_approval(ApprovalRegister(), request_id="APR-1", reference="X",
                         actor="Maker", reason="Review", at=datetime(2026,11,3))

def test_no_ledger_side_effect():
    from ledgerpoint.demo import build_demo
    book = build_demo().book
    before = len(book.ledger.history)
    reviewed = review_approval(sample(), request_id="APR-001", actor="Checker",
                               decision="Approved", note="Checked")
    assert reviewed.requests[0].status == "Approved"
    assert len(book.ledger.history) == before

def test_review_request_id_case_insensitive_and_canonical_event():
    result = review_approval(sample(), request_id="apr-001", actor="Checker",
                             decision="Approved", note="Checked")
    assert result.requests[0].status == "Approved"
    assert result.events[-1].request_id == "APR-001"

def test_blank_review_request_id_rejected():
    with pytest.raises(ValueError, match="Request ID"):
        review_approval(sample(), request_id="  ", actor="Checker",
                        decision="Approved", note="Checked")

def test_rejected_request_cannot_be_approved_later():
    rejected = review_approval(sample(), request_id="APR-001", actor="Checker",
                               decision="Rejected", note="Insufficient evidence")
    with pytest.raises(ValueError, match="already"):
        review_approval(rejected, request_id="APR-001", actor="Other",
                        decision="Approved", note="Override")
