from decimal import Decimal
import pytest
from ledgerpoint.book import LedgerBook
from ledgerpoint.ledger import Entry

def test_post_and_trial_balance():
    book = LedgerBook()
    book.post("J-001", [Entry("1000", debit=Decimal("250.00")), Entry("3000", credit=Decimal("250.00"))])
    assert book.trial_balance()["1000"] == Decimal("250.00")
    assert book.trial_balance()["3000"] == Decimal("-250.00")
    assert book.is_balanced()

def test_unknown_account_rejected_without_posting():
    book = LedgerBook()
    with pytest.raises(ValueError, match="Unknown"):
        book.post("J-002", [Entry("9999", debit=Decimal("10")), Entry("4000", credit=Decimal("10"))])
    assert not book.journals

def test_duplicate_journal_id_rejected():
    book = LedgerBook()
    lines = [Entry("1000", debit=Decimal("10")), Entry("3000", credit=Decimal("10"))]
    book.post("J-001", lines)
    with pytest.raises(ValueError, match="already used"):
        book.post("J-001", lines)
    assert len(book.journals) == 1

def test_multiple_journals_balance():
    book = LedgerBook()
    book.post("J-001", [Entry("1100", debit=Decimal("120")), Entry("4000", credit=Decimal("120"))])
    book.post("J-002", [Entry("1000", debit=Decimal("50")), Entry("1100", credit=Decimal("50"))])
    assert book.trial_balance()["1100"] == Decimal("70")
    assert book.is_balanced()
