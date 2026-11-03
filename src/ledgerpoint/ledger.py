"""Minimal, auditable double-entry journal foundation (EUR amounts)."""
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Entry:
    account: str
    debit: Decimal = Decimal('0')
    credit: Decimal = Decimal('0')


def validate_journal(entries: list[Entry]) -> None:
    if len(entries) < 2:
        raise ValueError('A journal requires at least two lines')
    if any(not e.account or e.debit < 0 or e.credit < 0 or (e.debit and e.credit) or (not e.debit and not e.credit) for e in entries):
        raise ValueError('Invalid journal line')
    if any(x.as_tuple().exponent < -2 for e in entries for x in (e.debit, e.credit)):
        raise ValueError('EUR amounts must have at most two decimal places')
    if sum((e.debit for e in entries), Decimal('0')) != sum((e.credit for e in entries), Decimal('0')):
        raise ValueError('Journal is not balanced')
