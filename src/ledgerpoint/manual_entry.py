"""Strictly validated fictional manual journals for a session-only sandbox."""
from datetime import date
from decimal import Decimal, InvalidOperation
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.ledger import Entry

def parse_eur(value: str) -> Decimal:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Amount is required")
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid EUR amount") from None
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError("Amount must be a non-negative EUR value with at most two decimals")
    return amount

def make_lines(debit_account: str, credit_account: str, amount_text: str) -> list[Entry]:
    amount = parse_eur(amount_text)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    if debit_account == credit_account:
        raise ValueError("Debit and credit accounts must differ")
    return [Entry(debit_account, debit=amount), Entry(credit_account, credit=amount)]

def post_manual(book: ControlledLedger, journal_id: str, posting_date: date,
                description: str, debit_account: str, credit_account: str,
                amount_text: str):
    if not journal_id or not journal_id.strip() or not journal_id.strip().startswith("MAN-"):
        raise ValueError("Manual journal ID must begin with MAN-")
    lines = make_lines(debit_account, credit_account, amount_text)
    return book.post(journal_id.strip(), posting_date, description.strip(), lines)
