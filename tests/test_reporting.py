from datetime import date
from decimal import Decimal as D
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.ledger import Entry
from ledgerpoint.reporting import trial_balance, profit_and_loss, balance_sheet

OCT = date(2026, 10, 31)
NOV = date(2026, 11, 30)

def example_book():
    b = ControlledLedger()
    b.post("CAP", OCT, "Capital introduced",
           [Entry("1000", debit=D("1000")), Entry("3000", credit=D("1000"))])
    b.post("REV", OCT, "Service revenue",
           [Entry("1100", debit=D("500")), Entry("4000", credit=D("500"))])
    b.post("EXP", OCT, "Operating cost",
           [Entry("5000", debit=D("200")), Entry("1000", credit=D("200"))])
    return b

def test_trial_balance_totals_equal():
    rows = trial_balance(example_book())
    assert sum((r.debit for r in rows), D("0")) == sum((r.credit for r in rows), D("0"))

def test_trial_balance_account_names():
    rows = trial_balance(example_book())
    assert next(r for r in rows if r.code == "1000").name == "Bank"

def test_profit_and_loss():
    p = profit_and_loss(example_book())
    assert (p.revenue, p.expenses, p.net_profit) == (D("500"), D("200"), D("300"))

def test_balance_sheet():
    s = balance_sheet(example_book())
    assert s.assets == D("1300")
    assert s.liabilities == 0
    assert s.contributed_equity == D("1000")
    assert s.retained_profit == D("300")
    assert s.balanced

def test_empty_book_reports_zero():
    b = ControlledLedger()
    assert profit_and_loss(b).net_profit == 0
    assert balance_sheet(b).balanced

def test_as_of_excludes_future_revenue():
    b = example_book()
    b.post("NEXT", NOV, "Next month sale",
           [Entry("1100", debit=D("50")), Entry("4000", credit=D("50"))])
    assert profit_and_loss(b, OCT).revenue == D("500")
    assert profit_and_loss(b, NOV).revenue == D("550")

def test_liability_on_balance_sheet():
    b = example_book()
    b.post("BILL", OCT, "Unpaid supplier",
           [Entry("5000", debit=D("100")), Entry("2000", credit=D("100"))])
    s = balance_sheet(b)
    assert s.liabilities == D("100")
    assert s.retained_profit == D("200")
    assert s.balanced

def test_loss_reduces_equity():
    b = ControlledLedger()
    b.post("LOSS", OCT, "Expense on credit",
           [Entry("5000", debit=D("150")), Entry("2000", credit=D("150"))])
    s = balance_sheet(b)
    assert s.retained_profit == D("-150")
    assert s.total_equity == D("-150")
    assert s.balanced

def test_reversal_updates_reports():
    b = example_book()
    b.reverse("REV", "REV-R", NOV, "Correct revenue")
    assert profit_and_loss(b, OCT).revenue == D("500")
    assert profit_and_loss(b, NOV).revenue == 0

def test_credit_balance_shown_in_credit_column():
    rows = trial_balance(example_book())
    revenue = next(r for r in rows if r.code == "4000")
    assert revenue.debit == 0
    assert revenue.credit == D("500")
