from datetime import date
from decimal import Decimal as D
import pytest
from ledgerpoint.invoices import Invoice, InvoiceKind
from ledgerpoint.settlements import SettlementBook, Party

DAY = date(2026, 10, 1)
DUE = date(2026, 10, 31)
KEY = (InvoiceKind.SALES, "c001", "inv-1")

def setup(kind=InvoiceKind.SALES):
    b = SettlementBook()
    b.add_party(Party("C001", "Fictional Client", kind))
    b.add_invoice(Invoice("INV-1", kind, "C001", DAY, DUE, D("100"), D("0.23")))
    key = (kind, "c001", "inv-1")
    return b, key

def test_sales_receipt_reduces_debtor_and_increases_bank():
    b, k = setup()
    b.allocate("P1", k, D("40"), date(2026, 10, 15))
    assert b.outstanding(k) == D("83")
    assert b.ledger.trial_balance()["1000"] == D("40")
    assert b.ledger.trial_balance()["1100"] == D("83")

def test_two_part_payments_settle_invoice():
    b, k = setup()
    b.allocate("P1", k, D("40"), date(2026, 10, 15))
    b.allocate("P2", k, D("83"), date(2026, 10, 20))
    assert b.outstanding(k) == 0

def test_purchase_payment_reduces_creditor_and_bank():
    b, k = setup(InvoiceKind.PURCHASE)
    b.allocate("P1", k, D("23"), date(2026, 10, 15))
    assert b.outstanding(k) == D("100")
    assert b.ledger.trial_balance()["2000"] == D("-100")
    assert b.ledger.trial_balance()["1000"] == D("-23")

def test_overpayment_rejected_without_posting():
    b, k = setup()
    with pytest.raises(ValueError, match="exceeds"):
        b.allocate("P1", k, D("124"), date(2026, 10, 15))
    assert len(b.ledger.history) == 1

def test_duplicate_payment_rejected():
    b, k = setup()
    b.allocate("P1", k, D("10"), date(2026, 10, 15))
    with pytest.raises(ValueError, match="already used"):
        b.allocate("P1", k, D("10"), date(2026, 10, 16))

def test_unknown_party_rejected():
    b = SettlementBook()
    with pytest.raises(ValueError, match="Unknown"):
        b.add_invoice(Invoice("INV-1", InvoiceKind.SALES, "C001", DAY, DUE, D("100"), D("0")))

def test_duplicate_invoice_rejected():
    b, k = setup()
    with pytest.raises(ValueError, match="Duplicate invoice"):
        b.add_invoice(b.invoices[k])

def test_as_of_outstanding_excludes_future_payment():
    b, k = setup()
    b.allocate("P1", k, D("40"), date(2026, 11, 5))
    assert b.outstanding(k, date(2026, 10, 31)) == D("123")

def test_ageing_buckets():
    b, k = setup()
    assert b.ageing(date(2026, 10, 15))["not_due"] == D("123")
    assert b.ageing(date(2026, 11, 15))["0-30"] == D("123")
    assert b.ageing(date(2027, 3, 1))["90+"] == D("123")

def test_closed_period_prevents_allocation():
    b, k = setup()
    b.ledger.close_period("2026-10")
    with pytest.raises(ValueError, match="closed"):
        b.allocate("P1", k, D("10"), date(2026, 10, 15))
    assert not b.allocations

def test_unbalanced_never_posted():
    b, k = setup()
    b.allocate("P1", k, D("10"), date(2026, 10, 15))
    assert sum(b.ledger.trial_balance().values()) == 0
