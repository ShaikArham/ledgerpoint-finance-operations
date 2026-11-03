import csv
from io import StringIO
from decimal import Decimal as D
from ledgerpoint.demo import build_demo
from ledgerpoint.exports import trial_balance_csv, reconciliation_csv
from ledgerpoint.reporting import trial_balance

def rows(text):
    return list(csv.DictReader(StringIO(text)))

def test_demo_invoice_balances():
    demo = build_demo()
    invoices = demo.book.invoices
    sales = next(k for k in invoices if k[0].value == "sales")
    purchase = next(k for k in invoices if k[0].value == "purchase")
    assert demo.book.outstanding(sales) == D("730.00")
    assert demo.book.outstanding(purchase) == D("0.00")

def test_demo_profit():
    demo = build_demo()
    assert demo.profit_and_loss.revenue == D("1000.00")
    assert demo.profit_and_loss.expenses == D("300.00")
    assert demo.profit_and_loss.net_profit == D("700.00")

def test_demo_balance_sheet():
    assert build_demo().balance_sheet.balanced

def test_demo_bank_and_receivables():
    balances = build_demo().book.ledger.trial_balance()
    assert balances["1000"] == D("131.00")
    assert balances["1100"] == D("730.00")

def test_demo_reconciliation_exceptions():
    statuses = {i.reference: i.status for i in build_demo().reconciliation}
    assert statuses == {"RCPT-001": "matched", "PMT-001": "matched",
                        "UNKNOWN-001": "bank_only"}

def test_demo_monthly_reporting():
    assert build_demo().october.profit == D("700.00")

def test_trial_balance_csv_export():
    demo = build_demo()
    exported = rows(trial_balance_csv(trial_balance(demo.book.ledger)))
    assert any(r["account_code"] == "1100" and r["debit_eur"] == "730.00"
               for r in exported)

def test_reconciliation_csv_export():
    exported = rows(reconciliation_csv(build_demo().reconciliation))
    assert any(r["reference"] == "UNKNOWN-001" and r["status"] == "bank_only"
               for r in exported)

def test_export_has_expected_headers():
    demo = build_demo()
    assert trial_balance_csv(trial_balance(demo.book.ledger)).splitlines()[0] == (
        "account_code,account_name,debit_eur,credit_eur")

def test_demo_is_deterministic():
    a, b = build_demo(), build_demo()
    assert a.profit_and_loss == b.profit_and_loss
    assert a.reconciliation == b.reconciliation
