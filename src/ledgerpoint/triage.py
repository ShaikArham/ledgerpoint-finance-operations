"""Explain reconciliation exceptions without altering the ledger."""
from dataclasses import dataclass
from ledgerpoint.reconciliation import ReconciliationItem

@dataclass(frozen=True)
class Investigation:
    reference: str
    status: str
    explanation: str
    next_action: str
    resolved: bool

GUIDANCE = {
    "matched": ("Bank and ledger amounts match by reference.", "No further action for this match.", True),
    "bank_only": ("The bank statement has a transaction with no matching posted payment.", "Check supporting documents, bank fees and the reference. Post a verified transaction through the controlled ledger before rerunning reconciliation.", False),
    "ledger_only": ("A posted payment has no matching bank statement transaction.", "Verify payment status, statement coverage and reference before investigating timing differences.", False),
    "amount_mismatch": ("The reference exists in both sources but amounts differ.", "Compare bank and ledger amounts, supporting documents and any fees. Correct verified source data and rerun reconciliation.", False),
    "duplicate_bank_reference": ("The bank statement repeats a reference.", "Review the individual bank lines and resolve the duplicate or reference collision before matching.", False),
}

def investigate(item: ReconciliationItem) -> Investigation:
    if item.status not in GUIDANCE:
        raise ValueError(f"Unknown reconciliation status: {item.status}")
    explanation, next_action, resolved = GUIDANCE[item.status]
    return Investigation(item.reference, item.status, explanation, next_action, resolved)
