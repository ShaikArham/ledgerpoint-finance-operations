from datetime import date
from decimal import Decimal
import pytest
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.ledger import Entry

D = Decimal
DAY = date(2026, 10, 31)

def sample():
    return [Entry("1000", debit=D("250.00")), Entry("3000", credit=D("250.00"))]

def test_post_and_history():
    book = ControlledLedger()
    posted = book.post("J1", DAY, "Capital deposit", sample())
    assert posted.journal_id == "J1"
    assert len(book.history) == 1
    assert book.trial_balance()["1000"] == D("250.00")

def test_reversal_preserves_original_and_nets_zero():
    book = ControlledLedger()
    book.post("J1", DAY, "Capital deposit", sample())
    reversal = book.reverse("J1", "R1", DAY, "Correction")
    assert reversal.reversal_of == "J1"
    assert len(book.history) == 2
    assert all(amount == 0 for amount in book.trial_balance().values())

def test_duplicate_reversal_rejected():
    book = ControlledLedger()
    book.post("J1", DAY, "Capital deposit", sample())
    book.reverse("J1", "R1", DAY, "Correction")
    with pytest.raises(ValueError, match="already reversed"):
        book.reverse("J1", "R2", DAY, "Second correction")

def test_closed_period_rejects_posting_and_reversal():
    book = ControlledLedger()
    book.post("J1", DAY, "Capital deposit", sample())
    book.close_period("2026-10")
    with pytest.raises(ValueError, match="closed"):
        book.post("J2", DAY, "Another deposit", sample())
    with pytest.raises(ValueError, match="closed"):
        book.reverse("J1", "R1", DAY, "Correction")

def test_reversal_in_open_next_month():
    book = ControlledLedger()
    book.post("J1", DAY, "Capital deposit", sample())
    book.close_period("2026-10")
    book.reverse("J1", "R1", date(2026, 11, 1), "Correction")
    assert len(book.history) == 2

def test_invalid_account_does_not_post():
    book = ControlledLedger()
    with pytest.raises(ValueError, match="Unknown"):
        book.post("J1", DAY, "Invalid", [
            Entry("9999", debit=D("10")), Entry("3000", credit=D("10"))])
    assert book.history == ()

def test_wrong_reversal_lines_rejected():
    book = ControlledLedger()
    book.post("J1", DAY, "Capital deposit", sample())
    with pytest.raises(ValueError, match="do not match"):
        book.post("R1", DAY, "Bad reversal", sample(), reversal_of="J1")
    assert len(book.history) == 1

def test_as_of_trial_balance():
    book = ControlledLedger()
    book.post("J1", DAY, "Capital deposit", sample())
    book.reverse("J1", "R1", date(2026, 11, 1), "Correction")
    assert book.trial_balance(through=DAY)["1000"] == D("250.00")
    assert book.trial_balance(through=date(2026, 11, 1))["1000"] == D("0.00")

def test_duplicate_journal_id_rejected():
    book = ControlledLedger()
    book.post("J1", DAY, "Capital deposit", sample())
    with pytest.raises(ValueError, match="already used"):
        book.post("J1", DAY, "Repeat", sample())

def test_invalid_period_rejected():
    with pytest.raises(ValueError, match="YYYY-MM"):
        ControlledLedger().close_period("2026-13")
