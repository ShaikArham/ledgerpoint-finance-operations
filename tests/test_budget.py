from decimal import Decimal as D
import pytest
from ledgerpoint.management import MonthlyResult
from ledgerpoint.budget import parse_budget, compare_budget, forecast

BASE = MonthlyResult("2026-10", D("1000"), D("300"), D("700"))

def test_budget_variances():
    result = compare_budget(BASE, D("1200"), D("250"))
    assert result.revenue_variance == D("-200")
    assert result.expense_variance == D("50")
    assert result.profit_budget == D("950")
    assert result.profit_variance == D("-250")

def test_forecast_scenario():
    result = forecast(BASE, 10, 20)
    assert (result.revenue, result.expenses, result.profit) == (D("1100.00"), D("360.00"), D("740.00"))

def test_forecast_floor():
    result = forecast(BASE, -100, -100)
    assert result.profit == 0

@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "1.234", "", "not money"])
def test_bad_budget_rejected(value):
    with pytest.raises(ValueError):
        parse_budget(value)

def test_zero_budget_allowed():
    assert parse_budget("0.00") == D("0.00")

def test_bad_forecast_bounds():
    with pytest.raises(ValueError):
        forecast(BASE, 201, 0)
    with pytest.raises(ValueError):
        forecast(BASE, 0, -101)

def test_negative_budget_rejected():
    with pytest.raises(ValueError):
        compare_budget(BASE, D("-1"), D("100"))
