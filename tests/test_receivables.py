"""Invoice positions use the selected reporting date, not today's date."""
from datetime import date
from decimal import Decimal
from ledgerpoint.demo import build_demo
from ledgerpoint.receivables import invoice_positions

def test_october_open_receivable():
    positions = invoice_positions(build_demo().book, date(2026, 10, 31))
    assert len(positions) == 1
    assert positions[0].reference == "SALE-001"
    assert positions[0].outstanding == Decimal("730.00")
    assert positions[0].bucket == "Not due"

def test_due_date_is_zero_days_overdue():
    positions = invoice_positions(build_demo().book, date(2026, 11, 4))
    assert positions[0].days_overdue == 0
    assert positions[0].bucket == "0–30 days"

def test_aged_invoice():
    positions = invoice_positions(build_demo().book, date(2027, 1, 5))
    assert positions[0].bucket == "61–90 days"
    assert positions[0].days_overdue == 62

def test_no_invoices_before_issuance():
    assert invoice_positions(build_demo().book, date(2026, 10, 1)) == ()
