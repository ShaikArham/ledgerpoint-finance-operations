"""Reference-based reconciliation for fictional bank statement data.

This is a deterministic demonstration, not automated bank connectivity.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from ledgerpoint.settlements import SettlementBook

@dataclass(frozen=True)
class BankTransaction:
    reference: str
    booked_on: date
    amount: Decimal  # positive = money in, negative = money out

@dataclass(frozen=True)
class ReconciliationItem:
    reference: str
    status: str
    ledger_amount: Decimal | None
    bank_amount: Decimal | None

def reconcile(book: SettlementBook, transactions: list[BankTransaction],
              through: date) -> list[ReconciliationItem]:
    """Match exact payment IDs against bank references up to a cutoff date.

    Missing entries, duplicates and amount mismatches remain exceptions.
    """
    statement: dict[str, BankTransaction] = {}
    duplicates: set[str] = set()
    for transaction in transactions:
        if not transaction.reference.strip():
            raise ValueError("Bank reference required")
        if not transaction.amount.is_finite() or transaction.amount == 0 or transaction.amount.as_tuple().exponent < -2:
            raise ValueError("Invalid bank amount")
        if transaction.booked_on > through:
            continue
        if transaction.reference in statement:
            duplicates.add(transaction.reference)
        else:
            statement[transaction.reference] = transaction

    expected: dict[str, Decimal] = {}
    for allocation in book.allocations:
        if allocation.paid_on <= through:
            direction = 1 if allocation.invoice_key[0].value == "sales" else -1
            expected[allocation.payment_id] = allocation.amount * direction

    items: list[ReconciliationItem] = []
    for reference in sorted(set(expected) | set(statement)):
        ledger_amount = expected.get(reference)
        bank_amount = statement[reference].amount if reference in statement else None
        if reference in duplicates:
            status = "duplicate_bank_reference"
        elif ledger_amount is None:
            status = "bank_only"
        elif bank_amount is None:
            status = "ledger_only"
        elif ledger_amount != bank_amount:
            status = "amount_mismatch"
        else:
            status = "matched"
        items.append(ReconciliationItem(reference, status, ledger_amount, bank_amount))
    return items

def reconciliation_summary(items: list[ReconciliationItem]) -> dict[str, int]:
    statuses = ("matched", "ledger_only", "bank_only", "amount_mismatch", "duplicate_bank_reference")
    return {status: sum(item.status == status for item in items) for status in statuses}
