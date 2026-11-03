"""Tests for session-only manual journals."""
from datetime import date
from decimal import Decimal
import pytest
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.manual_entry import make_lines, parse_eur, post_manual

@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "1.234", "abc", "", " "])
def test_invalid_amount(value):
    with pytest.raises(ValueError):
        parse_eur(value)

def test_valid_amount():
    assert parse_eur("12.50") == Decimal("12.50")

def test_accounts_must_differ():
    with pytest.raises(ValueError, match="differ"):
        make_lines("1000", "1000", "12")

def test_valid_post_and_balance():
    book = ControlledLedger()
    posted = post_manual(book, "MAN-001", date(2026, 10, 22), "Fictional adjustment", "5000", "1000", "12.00")
    assert posted.journal_id == "MAN-001"
    assert sum(book.trial_balance().values()) == 0
    assert book.trial_balance()["5000"] == Decimal("12.00")

def test_duplicate_id_rejected():
    book = ControlledLedger()
    args = ("MAN-001", date(2026, 10, 22), "Adjustment", "5000", "1000", "12.00")
    post_manual(book, *args)
    with pytest.raises(ValueError, match="already used"):
        post_manual(book, *args)
    assert len(book.history) == 1

def test_closed_period_rejected():
    book = ControlledLedger()
    book.close_period("2026-10")
    with pytest.raises(ValueError, match="closed"):
        post_manual(book, "MAN-001", date(2026, 10, 22), "Adjustment", "5000", "1000", "12")
    assert not book.history

def test_unknown_account_rejected():
    with pytest.raises(ValueError, match="Unknown account"):
        post_manual(ControlledLedger(), "MAN-001", date(2026, 10, 22), "Adjustment", "9999", "1000", "12")

def test_bad_id_rejected():
    with pytest.raises(ValueError, match="MAN-"):
        post_manual(ControlledLedger(), "INV-001", date(2026, 10, 22), "Adjustment", "5000", "1000", "12")

def test_blank_description_rejected_without_posting():
    book = ControlledLedger()
    with pytest.raises(ValueError, match="Description required"):
        post_manual(book, "MAN-001", date(2026, 10, 22), " ", "5000", "1000", "12")
    assert not book.history

def test_invalid_amount_does_not_mutate_ledger():
    book = ControlledLedger()
    with pytest.raises(ValueError, match="two decimals"):
        post_manual(book, "MAN-001", date(2026, 10, 22), "Test", "5000", "1000", "12.345")
    assert not book.history

def test_missing_id_has_specific_message():
    book = ControlledLedger()
    with pytest.raises(ValueError, match="MAN-"):
        post_manual(book, "", date(2026, 10, 22), "Test", "5000", "1000", "12")
    assert not book.history
