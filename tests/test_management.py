from datetime import date
from decimal import Decimal as D
import pytest
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.ledger import Entry
from ledgerpoint.management import monthly_result, budget_variance, month_end_checks, month_bounds

def sample():
    b = ControlledLedger()
    b.post("OCT", date(2026,10,10), "October revenue",
           [Entry("1100", debit=D("500")), Entry("4000", credit=D("500"))])
    b.post("OCT-E", date(2026,10,20), "October expense",
           [Entry("5000", debit=D("100")), Entry("2000", credit=D("100"))])
    b.post("NOV", date(2026,11,10), "November revenue",
           [Entry("1100", debit=D("200")), Entry("4000", credit=D("200"))])
    return b

def test_october_monthly_profit():
    r = monthly_result(sample(), "2026-10")
    assert (r.revenue, r.expenses, r.profit) == (D("500"), D("100"), D("400"))

def test_november_is_separate():
    r = monthly_result(sample(), "2026-11")
    assert (r.revenue, r.expenses, r.profit) == (D("200"), D("0"), D("200"))

def test_empty_month():
    assert monthly_result(sample(), "2026-12").profit == 0

def test_variance_positive():
    v = budget_variance(D("110"), D("100"))
    assert (v.difference, v.percentage) == (D("10"), D("10"))

def test_variance_negative():
    assert budget_variance(D("80"), D("100")).difference == D("-20")

def test_zero_budget_percentage_not_defined():
    assert budget_variance(D("20"), D("0")).percentage is None

def test_invalid_month():
    with pytest.raises(ValueError, match="YYYY-MM"):
        month_bounds("2026-13")

def test_leap_year_end():
    assert month_bounds("2028-02")[1] == date(2028,2,29)

def test_close_checks_before_lock():
    checks = month_end_checks(sample(), "2026-10")
    assert [c.passed for c in checks] == [True, True, True, False]

def test_close_checks_after_lock():
    b = sample()
    b.close_period("2026-10")
    assert all(c.passed for c in month_end_checks(b, "2026-10"))

def test_no_activity_check():
    checks = month_end_checks(sample(), "2026-12")
    assert next(c for c in checks if c.name == "Period has entries").passed is False
