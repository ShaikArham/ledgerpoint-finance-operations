"""Chart of accounts for the fictional LedgerPoint business."""
from dataclasses import dataclass
from enum import Enum

class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

@dataclass(frozen=True)
class Account:
    code: str
    name: str
    kind: AccountType

CHART = {
    "1000": Account("1000", "Bank", AccountType.ASSET),
    "1100": Account("1100", "Trade receivables", AccountType.ASSET),
    "2000": Account("2000", "Trade payables", AccountType.LIABILITY),
    "2100": Account("2100", "VAT control", AccountType.LIABILITY),
    "3000": Account("3000", "Owner capital", AccountType.EQUITY),
    "4000": Account("4000", "Sales revenue", AccountType.REVENUE),
    "5000": Account("5000", "Operating expenses", AccountType.EXPENSE),
}
