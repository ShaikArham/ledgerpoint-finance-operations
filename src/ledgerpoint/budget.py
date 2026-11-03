"""Illustrative monthly budget and deterministic what-if forecast."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from ledgerpoint.management import MonthlyResult, budget_variance

CENT = Decimal("0.01")

def parse_budget(value: str) -> Decimal:
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError("Enter a valid budget amount") from None
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError("Budget must be non-negative with at most two decimals")
    return amount

@dataclass(frozen=True)
class BudgetReport:
    revenue_actual: Decimal
    revenue_budget: Decimal
    expense_actual: Decimal
    expense_budget: Decimal
    profit_actual: Decimal
    profit_budget: Decimal
    revenue_variance: Decimal
    expense_variance: Decimal
    profit_variance: Decimal

def compare_budget(actual: MonthlyResult, revenue_budget: Decimal, expense_budget: Decimal) -> BudgetReport:
    for value in (revenue_budget, expense_budget):
        if not value.is_finite() or value < 0:
            raise ValueError("Budgets must be finite and non-negative")
    profit_budget = revenue_budget - expense_budget
    return BudgetReport(
        actual.revenue, revenue_budget, actual.expenses, expense_budget,
        actual.profit, profit_budget,
        budget_variance(actual.revenue, revenue_budget).difference,
        budget_variance(actual.expenses, expense_budget).difference,
        budget_variance(actual.profit, profit_budget).difference,
    )

def forecast(actual: MonthlyResult, revenue_change_pct: int, expense_change_pct: int) -> MonthlyResult:
    if not -100 <= revenue_change_pct <= 200 or not -100 <= expense_change_pct <= 200:
        raise ValueError("Scenario changes must be between -100% and 200%")
    revenue = (actual.revenue * (Decimal(100 + revenue_change_pct) / 100)).quantize(CENT, rounding=ROUND_HALF_UP)
    expenses = (actual.expenses * (Decimal(100 + expense_change_pct) / 100)).quantize(CENT, rounding=ROUND_HALF_UP)
    return MonthlyResult(actual.month + " (scenario)", revenue, expenses, revenue - expenses)
