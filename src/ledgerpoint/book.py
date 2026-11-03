"""In-memory posting engine for an educational fictional ledger.

Not a production ledger: persistence, immutable audit history, reversals,
period locks and user authorisation will be added in later milestones.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from ledgerpoint.accounts import Account, CHART
from ledgerpoint.ledger import Entry, validate_journal

@dataclass
class LedgerBook:
    accounts: dict[str, Account] = field(default_factory=lambda: dict(CHART))
    journals: list[tuple[str, tuple[Entry, ...]]] = field(default_factory=list)

    def post(self, journal_id: str, entries: list[Entry]) -> None:
        if not journal_id or any(jid == journal_id for jid, _ in self.journals):
            raise ValueError("Journal ID missing or already used")
        validate_journal(entries)
        if any(e.account not in self.accounts for e in entries):
            raise ValueError("Unknown account code")
        self.journals.append((journal_id, tuple(entries)))

    def trial_balance(self) -> dict[str, Decimal]:
        """Debit-positive, credit-negative signed balances by account."""
        balances = {code: Decimal("0.00") for code in self.accounts}
        for _, lines in self.journals:
            for line in lines:
                balances[line.account] += line.debit - line.credit
        return balances

    def is_balanced(self) -> bool:
        return sum(self.trial_balance().values(), Decimal("0")) == 0
