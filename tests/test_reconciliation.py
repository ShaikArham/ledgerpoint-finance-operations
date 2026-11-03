from datetime import date
from decimal import Decimal as D
import pytest
from ledgerpoint.invoices import Invoice, InvoiceKind
from ledgerpoint.settlements import SettlementBook, Party
from ledgerpoint.reconciliation import BankTransaction, reconcile, reconciliation_summary

DAY = date(2026, 10, 15)

def paid_book(kind=InvoiceKind.SALES):
    b = SettlementBook()
    b.add_party(Party("P1", "Fictional Party", kind))
    invoice = Invoice("INV-1", kind, "P1", date(2026, 10, 1),
                      date(2026, 10, 31), D("100"), D("0"))
    b.add_invoice(invoice)
    b.allocate("PAY-1", b.key(invoice), D("60"), DAY)
    return b

def bank(ref="PAY-1", amount=D("60"), day=DAY):
    return BankTransaction(ref, day, amount)

def test_exact_receipt_match():
    items = reconcile(paid_book(), [bank()], DAY)
    assert [(i.reference, i.status) for i in items] == [("PAY-1", "matched")]

def test_purchase_payment_negative_bank_amount():
    items = reconcile(paid_book(InvoiceKind.PURCHASE), [bank(amount=D("-60"))], DAY)
    assert items[0].status == "matched"

def test_missing_bank_entry():
    items = reconcile(paid_book(), [], DAY)
    assert items[0].status == "ledger_only"

def test_unexpected_bank_entry():
    items = reconcile(SettlementBook(), [bank()], DAY)
    assert items[0].status == "bank_only"

def test_amount_mismatch():
    items = reconcile(paid_book(), [bank(amount=D("59.99"))], DAY)
    assert items[0].status == "amount_mismatch"

def test_duplicate_statement_reference():
    items = reconcile(paid_book(), [bank(), bank()], DAY)
    assert items[0].status == "duplicate_bank_reference"

def test_cutoff_excludes_future_bank_item():
    items = reconcile(paid_book(), [bank(day=date(2026, 11, 1))], DAY)
    assert items[0].status == "ledger_only"

def test_cutoff_excludes_future_payment():
    b = paid_book()
    items = reconcile(b, [bank()], date(2026, 10, 1))
    assert items == []

def test_reject_invalid_bank_amount():
    with pytest.raises(ValueError, match="Invalid bank amount"):
        reconcile(SettlementBook(), [bank(amount=D("0"))], DAY)

def test_summary_counts():
    items = reconcile(paid_book(), [bank(), bank(ref="OTHER")], DAY)
    summary = reconciliation_summary(items)
    assert summary["matched"] == 1
    assert summary["bank_only"] == 1
    assert summary["amount_mismatch"] == 0
