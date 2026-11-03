"""Read-only invoice ageing and suggested follow-up for fictional invoices."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from ledgerpoint.invoices import Invoice
from ledgerpoint.settlements import SettlementBook

@dataclass(frozen=True)
class InvoicePosition:
    reference: str
    party: str
    kind: str
    due_date: date
    outstanding: Decimal
    days_overdue: int
    bucket: str
    action: str

def invoice_positions(book: SettlementBook, as_of: date) -> tuple[InvoicePosition, ...]:
    positions = []
    for key, invoice in book.invoices.items():
        if invoice.issue_date > as_of:
            continue
        balance = book.outstanding(key, as_of)
        if balance <= 0:
            continue
        days = max(0, (as_of - invoice.due_date).days)
        raw_days = (as_of - invoice.due_date).days
        bucket = ("Not due" if raw_days < 0 else "0–30 days" if raw_days <= 30
                  else "31–60 days" if raw_days <= 60 else "61–90 days" if raw_days <= 90 else "90+ days")
        action = ("Monitor until due date" if raw_days < 0 else
                  "Review payment status and send a courteous reminder" if raw_days <= 30 else
                  "Follow up with the counterparty and investigate the delay")
        party = book.parties[(invoice.kind, invoice.party_id.casefold())].name
        positions.append(InvoicePosition(invoice.invoice_id, party, invoice.kind.value,
                                         invoice.due_date, balance, days, bucket, action))
    return tuple(sorted(positions, key=lambda p: (p.due_date, p.reference)))
