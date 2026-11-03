"""Simplified management reporting for fictional LedgerPoint data."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from ledgerpoint.accounts import AccountType
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.reporting import profit_and_loss

ZERO = Decimal("0.00")

@dataclass(frozen=True)
class MonthlyResult:
    month: str
    revenue: Decimal
    expenses: Decimal
    profit: Decimal

@dataclass(frozen=True)
class Variance:
    actual: Decimal
    budget: Decimal
    difference: Decimal
    percentage: Decimal | None

def month_bounds(month: str) -> tuple[date, date]:
    try:
        start = date.fromisoformat(month + "-01")
        if start.strftime("%Y-%m") != month:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("Month must be YYYY-MM") from None
    next_month = date(start.year + (start.month == 12),
                      start.month % 12 + 1, 1)
    from datetime import timedelta
    return start, next_month - timedelta(days=1)

def monthly_result(book: ControlledLedger, month: str) -> MonthlyResult:
    start, end = month_bounds(month)
    balances = {code: ZERO for code in book.accounts}
    for journal in book.history:
        if start <= journal.posting_date <= end:
            for line in journal.entries:
                balances[line.account] += line.debit - line.credit
    revenue = sum((-balances[code] for code, account in book.accounts.items()
                   if account.kind == AccountType.REVENUE), ZERO)
    expenses = sum((balances[code] for code, account in book.accounts.items()
                    if account.kind == AccountType.EXPENSE), ZERO)
    return MonthlyResult(month, revenue, expenses, revenue - expenses)

def budget_variance(actual: Decimal, budget: Decimal) -> Variance:
    if not actual.is_finite() or not budget.is_finite():
        raise ValueError("Finite amounts required")
    difference = actual - budget
    percentage = None if budget == 0 else (difference / abs(budget)) * 100
    return Variance(actual, budget, difference, percentage)

@dataclass(frozen=True)
class CloseCheck:
    name: str
    passed: bool
    details: str

def month_end_checks(book: ControlledLedger, month: str) -> tuple[CloseCheck, ...]:
    start, end = month_bounds(month)
    journals = [j for j in book.history if start <= j.posting_date <= end]
    balanced = sum(book.trial_balance(through=end).values(), ZERO) == 0
    unique = len({j.journal_id for j in book.history}) == len(book.history)
    return (
        CloseCheck("Trial balance", balanced, "Cumulative debits equal credits"),
        CloseCheck("Unique journal IDs", unique, "No repeated posted journal identifiers"),
        CloseCheck("Period has entries", bool(journals), f"{len(journals)} journals in {month}"),
        CloseCheck("Period locked", month in book.closed_periods, "Month is closed to new postings"),
    )
