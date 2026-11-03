"""Fictional invoice settlements and ageing, backed by the controlled ledger."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.invoices import Invoice, InvoiceKind, validate_invoice
from ledgerpoint.posting import post_invoice
from ledgerpoint.ledger import Entry

@dataclass(frozen=True)
class Party:
    party_id: str
    name: str
    kind: InvoiceKind

@dataclass(frozen=True)
class Allocation:
    payment_id: str
    invoice_key: tuple[InvoiceKind, str, str]
    amount: Decimal
    paid_on: date

@dataclass
class SettlementBook:
    ledger: ControlledLedger = field(default_factory=ControlledLedger)
    parties: dict[tuple[InvoiceKind, str], Party] = field(default_factory=dict)
    invoices: dict[tuple[InvoiceKind, str, str], Invoice] = field(default_factory=dict)
    allocations: list[Allocation] = field(default_factory=list)

    @staticmethod
    def key(invoice: Invoice) -> tuple[InvoiceKind, str, str]:
        return invoice.kind, invoice.party_id.casefold(), invoice.invoice_id.casefold()

    def add_party(self, party: Party) -> None:
        if not party.party_id.strip() or not party.name.strip():
            raise ValueError("Party ID and name required")
        key = (party.kind, party.party_id.casefold())
        if key in self.parties:
            raise ValueError("Duplicate party")
        self.parties[key] = party

    def add_invoice(self, invoice: Invoice) -> None:
        validate_invoice(invoice)
        key = self.key(invoice)
        if (invoice.kind, invoice.party_id.casefold()) not in self.parties:
            raise ValueError("Unknown customer or supplier")
        if key in self.invoices:
            raise ValueError("Duplicate invoice")
        post_invoice(self.ledger, invoice)
        self.invoices[key] = invoice

    def outstanding(self, key: tuple[InvoiceKind, str, str], as_of: date | None = None) -> Decimal:
        invoice = self.invoices[key]
        total = sum((a.amount for a in self.allocations
                     if a.invoice_key == key and (as_of is None or a.paid_on <= as_of)),
                    Decimal("0.00"))
        return invoice.gross_amount - total

    def allocate(self, payment_id: str, key: tuple[InvoiceKind, str, str],
                 amount: Decimal, paid_on: date) -> None:
        if key not in self.invoices:
            raise ValueError("Unknown invoice")
        if not payment_id.strip() or any(a.payment_id == payment_id for a in self.allocations):
            raise ValueError("Payment ID missing or already used")
        if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
            raise ValueError("Invalid payment amount")
        invoice = self.invoices[key]
        if paid_on < invoice.issue_date:
            raise ValueError("Payment precedes invoice")
        if amount > self.outstanding(key):
            raise ValueError("Payment exceeds outstanding balance")
        if invoice.kind == InvoiceKind.SALES:
            lines = [Entry("1000", debit=amount), Entry("1100", credit=amount)]
        else:
            lines = [Entry("2000", debit=amount), Entry("1000", credit=amount)]
        self.ledger.post("PAY:" + payment_id, paid_on,
                         "Settlement of " + invoice.invoice_id, lines)
        self.allocations.append(Allocation(payment_id, key, amount, paid_on))

    def ageing(self, as_of: date) -> dict[str, Decimal]:
        buckets = {name: Decimal("0.00") for name in ("not_due", "0-30", "31-60", "61-90", "90+")}
        for key, invoice in self.invoices.items():
            if invoice.issue_date > as_of:
                continue
            balance = self.outstanding(key, as_of)
            if balance <= 0:
                continue
            overdue = (as_of - invoice.due_date).days
            bucket = ("not_due" if overdue < 0 else "0-30" if overdue <= 30
                      else "31-60" if overdue <= 60 else "61-90" if overdue <= 90 else "90+")
            buckets[bucket] += balance
        return buckets
