"""Payroll demo controls: no real Irish PAYE/USC/PRSI rates are inferred."""
from decimal import Decimal as D
import pytest
from ledgerpoint.payroll import PayrollInput, calculate_payroll, payroll_batch, money

def entry(employee="EMP-001", hours="40", rate="20", deduction="15"):
    return PayrollInput(employee, D(hours), D(rate), D(deduction))

def test_illustrative_payslip():
    slip = calculate_payroll(entry())
    assert (slip.gross, slip.illustrative_deduction, slip.net) == (
        D("800.00"), D("120.00"), D("680.00"))

def test_zero_deduction():
    assert calculate_payroll(entry(deduction="0")).net == D("800.00")

def test_full_deduction():
    assert calculate_payroll(entry(deduction="100")).net == D("0.00")

def test_rounding():
    slip = calculate_payroll(entry(hours="1.25", rate="11.11", deduction="10"))
    assert slip.gross == D("13.89")
    assert slip.illustrative_deduction == D("1.39")
    assert slip.net == D("12.50")

@pytest.mark.parametrize("hours,rate,deduction", [
    ("-1", "20", "15"), ("40", "-1", "15"), ("40", "20", "101"),
    ("NaN", "20", "15"), ("40", "Infinity", "15"),
    ("745", "20", "15"), ("40", "10001", "15"),
    ("1.234", "20", "15")
])
def test_invalid_inputs(hours, rate, deduction):
    with pytest.raises(ValueError):
        calculate_payroll(entry(hours=hours, rate=rate, deduction=deduction))

def test_blank_employee_rejected():
    with pytest.raises(ValueError, match="Employee reference"):
        calculate_payroll(entry(employee="  "))

def test_duplicate_employee_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        payroll_batch((entry("EMP-001"), entry("emp-001")))

def test_batch_totals():
    slips = payroll_batch((entry("EMP-001"), entry("EMP-002")))
    assert sum((s.net for s in slips), D("0")) == D("1360.00")

@pytest.mark.parametrize("value", ["NaN", "Infinity", "-2", "abc", ""])
def test_money_input_validation(value):
    with pytest.raises(ValueError):
        money(value, "Hours")
