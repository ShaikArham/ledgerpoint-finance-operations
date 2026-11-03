"""Read-only investigation guidance tests."""
import pytest
from decimal import Decimal
from ledgerpoint.reconciliation import ReconciliationItem
from ledgerpoint.triage import investigate

@pytest.mark.parametrize("status", ["matched", "bank_only", "ledger_only", "amount_mismatch", "duplicate_bank_reference"])
def test_all_known_statuses_have_guidance(status):
    result = investigate(ReconciliationItem("REF", status, None, Decimal("12.00")))
    assert result.reference == "REF"
    assert result.explanation
    assert result.next_action
    assert result.resolved == (status == "matched")

def test_unknown_status_rejected():
    with pytest.raises(ValueError, match="Unknown"):
        investigate(ReconciliationItem("REF", "other", None, None))

def test_bank_only_guidance_does_not_claim_posting():
    result = investigate(ReconciliationItem("UNKNOWN-001", "bank_only", None, Decimal("-12.00")))
    assert not result.resolved
    assert "verified" in result.next_action
