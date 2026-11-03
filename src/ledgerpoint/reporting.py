"""Financial statements from the fictional LedgerPoint controlled ledger.

Balances are debit-positive, credit-negative. Reports are cumulative as of a
date, not period-specific statutory financial statements.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from ledgerpoint.accounts import AccountType
from ledgerpoint.controlled import ControlledLedger

ZERO = Decimal("0.00")

@dataclass(frozen=True)
class TrialBalanceRow:
    code: str
    name: str
    debit: Decimal
    credit: Decimal

@dataclass(frozen=True)
class ProfitAndLoss:
    revenue: Decimal
    expenses: Decimal
    net_profit: Decimal

@dataclass(frozen=True)
class BalanceSheet:
    assets: Decimal
    liabilities: Decimal
    contributed_equity: Decimal
    retained_profit: Decimal
    total_equity: Decimal
    liabilities_and_equity: Decimal
    balanced: bool

def trial_balance(book: ControlledLedger, as_of: date | None = None) -> list[TrialBalanceRow]:
    balances = book.trial_balance(through=as_of)
    return [
        TrialBalanceRow(code, book.accounts[code].name,
                        max(amount, ZERO), max(-amount, ZERO))
        for code, amount in sorted(balances.items())
    ]

def profit_and_loss(book: ControlledLedger, as_of: date | None = None) -> ProfitAndLoss:
    balances = book.trial_balance(through=as_of)
    revenue = sum((-balances[code] for code, account in book.accounts.items()
                   if account.kind == AccountType.REVENUE), ZERO)
    expenses = sum((balances[code] for code, account in book.accounts.items()
                    if account.kind == AccountType.EXPENSE), ZERO)
    return ProfitAndLoss(revenue, expenses, revenue - expenses)

def balance_sheet(book: ControlledLedger, as_of: date | None = None) -> BalanceSheet:
    balances = book.trial_balance(through=as_of)
    def total(kind: AccountType, sign: int) -> Decimal:
        return sum((balances[code] * sign for code, account in book.accounts.items()
                    if account.kind == kind), ZERO)
    assets = total(AccountType.ASSET, 1)
    liabilities = total(AccountType.LIABILITY, -1)
    contributed = total(AccountType.EQUITY, -1)
    profit = profit_and_loss(book, as_of).net_profit
    equity = contributed + profit
    right = liabilities + equity
    return BalanceSheet(assets, liabilities, contributed, profit, equity,
                        right, assets == right)
