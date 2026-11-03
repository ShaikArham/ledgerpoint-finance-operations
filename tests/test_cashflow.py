from datetime import date
from decimal import Decimal as D
import pytest
from ledgerpoint.demo import build_demo
from ledgerpoint.cashflow import cash_flow, working_capital

def test_october_cash_movement_and_reconciliation():
    book = build_demo().book
    report = cash_flow(book, date(2026, 10, 1), date(2026, 10, 31))
    assert report.customer_receipts == D("500")
    assert report.supplier_payments == D("369")
    assert report.net_settlement_cash_flow == D("131")
    assert report.opening_bank_balance == D("0")
    assert report.closing_bank_balance == D("131")
    assert report.other_posted_bank_movements == D("0")
    assert report.closing_bank_balance - report.opening_bank_balance == (
        report.net_settlement_cash_flow + report.other_posted_bank_movements
    )

def test_working_capital_october():
    report = working_capital(build_demo().book, date(2026, 10, 31))
    assert report.trade_receivables == D("730")
    assert report.trade_payables == D("0")
    assert report.net_trade_working_capital == D("730")
    assert report.bank_balance == D("131")
    assert report.overdue_receivables == D("0")

def test_before_invoice_issue_is_empty():
    report = working_capital(build_demo().book, date(2026, 10, 1))
    assert report.trade_receivables == 0
    assert report.trade_payables == 0
    assert report.bank_balance == 0

def test_after_due_date_flags_overdue():
    report = working_capital(build_demo().book, date(2026, 11, 10))
    assert report.overdue_receivables == D("730")
    assert report.overdue_payables == 0

def test_invalid_date_range_rejected():
    with pytest.raises(ValueError, match="Start date"):
        cash_flow(build_demo().book, date(2026, 11, 1), date(2026, 10, 1))

def test_cash_flow_before_payments_is_zero():
    report = cash_flow(build_demo().book, date(2026, 10, 1), date(2026, 10, 10))
    assert report.net_settlement_cash_flow == 0
    assert report.closing_bank_balance == 0

def test_bank_only_exception_is_not_counted_as_posted_cash():
    book = build_demo().book
    report = cash_flow(book, date(2026, 10, 1), date(2026, 10, 31))
    # UNKNOWN-001 (-12) appears only in the fictional bank statement, not ledger.
    assert report.closing_bank_balance == D("131")
