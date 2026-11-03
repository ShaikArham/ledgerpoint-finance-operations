"""Controlled in-memory ledger for a fictional accounting demonstration.

Posted records are frozen and append-only within this process. This is NOT
durable storage or a tamper-proof audit log.
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from ledgerpoint.accounts import Account, CHART
from ledgerpoint.ledger import Entry, validate_journal

@dataclass(frozen=True)
class PostedJournal:
    journal_id: str
    posting_date: date
    description: str
    entries: tuple[Entry, ...]
    reversal_of: str | None = None

@dataclass
class ControlledLedger:
    accounts: dict[str, Account] = field(default_factory=lambda: dict(CHART))
    _history: list[PostedJournal] = field(default_factory=list, repr=False)
    _closed_periods: set[str] = field(default_factory=set, repr=False)

    @property
    def history(self) -> tuple[PostedJournal, ...]:
        return tuple(self._history)

    @property
    def closed_periods(self) -> frozenset[str]:
        return frozenset(self._closed_periods)

    def post(self, journal_id: str, posting_date: date, description: str,
             entries: list[Entry], reversal_of: str | None = None) -> PostedJournal:
        if not isinstance(posting_date, date) or isinstance(posting_date, __import__("datetime").datetime):
            raise ValueError("Posting date must be a calendar date")
        if not journal_id.strip():
            raise ValueError("Journal ID is required")
        if any(j.journal_id == journal_id for j in self._history):
            raise ValueError(f"Journal ID {journal_id} already used")
        if not description.strip():
            raise ValueError("Description required")
        if posting_date.strftime("%Y-%m") in self._closed_periods:
            raise ValueError("Accounting period is closed")
        validate_journal(entries)
        if any(e.account not in self.accounts for e in entries):
            raise ValueError("Unknown account")
        if reversal_of is not None:
            original = next((j for j in self._history if j.journal_id == reversal_of), None)
            if original is None or original.reversal_of is not None:
                raise ValueError("Invalid reversal target")
            if any(j.reversal_of == reversal_of for j in self._history):
                raise ValueError("Journal already reversed")
            expected = tuple(Entry(e.account, debit=e.credit, credit=e.debit)
                             for e in original.entries)
            if tuple(entries) != expected:
                raise ValueError("Reversal lines do not match original")
        journal = PostedJournal(journal_id, posting_date, description,
                                tuple(entries), reversal_of)
        self._history.append(journal)
        return journal

    def reverse(self, original_id: str, reversal_id: str,
                posting_date: date, reason: str) -> PostedJournal:
        original = next((j for j in self._history if j.journal_id == original_id), None)
        if original is None:
            raise ValueError("Original journal not found")
        if original.reversal_of is not None:
            raise ValueError("Cannot reverse a reversal")
        if not reason.strip():
            raise ValueError("Reversal reason required")
        lines = [Entry(e.account, debit=e.credit, credit=e.debit)
                 for e in original.entries]
        return self.post(reversal_id, posting_date, "Reversal: " + reason,
                         lines, reversal_of=original_id)

    def close_period(self, period: str) -> None:
        try:
            parsed = date.fromisoformat(period + "-01")
        except (ValueError, TypeError):
            raise ValueError("Period must be YYYY-MM") from None
        if parsed.strftime("%Y-%m") != period:
            raise ValueError("Period must be YYYY-MM")
        self._closed_periods.add(period)

    def trial_balance(self, through: date | None = None) -> dict[str, Decimal]:
        totals = {code: Decimal("0.00") for code in self.accounts}
        for journal in self._history:
            if through is None or journal.posting_date <= through:
                for line in journal.entries:
                    totals[line.account] += line.debit - line.credit
        return totals
