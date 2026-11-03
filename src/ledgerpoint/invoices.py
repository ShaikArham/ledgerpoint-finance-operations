"""Fictional invoice intake and validation; no statutory VAT advice."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum

CENT = Decimal("0.01")

class InvoiceKind(str, Enum):
    SALES = "sales"
    PURCHASE = "purchase"

@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    kind: InvoiceKind
    party_id: str
    issue_date: date
    due_date: date
    net_amount: Decimal
    vat_rate: Decimal
    currency: str = "EUR"

    @property
    def vat_amount(self) -> Decimal:
        return (self.net_amount * self.vat_rate).quantize(CENT, rounding=ROUND_HALF_UP)

    @property
    def gross_amount(self) -> Decimal:
        return self.net_amount + self.vat_amount

def validate_invoice(invoice: Invoice) -> None:
    if not invoice.invoice_id.strip() or not invoice.party_id.strip():
        raise ValueError("Invoice reference and party required")
    if not isinstance(invoice.kind, InvoiceKind):
        raise ValueError("Unknown invoice kind")
    if not isinstance(invoice.issue_date, date) or not isinstance(invoice.due_date, date):
        raise ValueError("Valid invoice dates required")
    if invoice.due_date < invoice.issue_date:
        raise ValueError("Due date precedes invoice date")
    if invoice.currency != "EUR":
        raise ValueError("Only EUR is supported")
    if not invoice.net_amount.is_finite() or invoice.net_amount <= 0 or invoice.net_amount.as_tuple().exponent < -2:
        raise ValueError("Invalid net amount")
    if not invoice.vat_rate.is_finite() or invoice.vat_rate < 0 or invoice.vat_rate > 1:
        raise ValueError("Invalid illustrative VAT rate")

@dataclass
class InvoiceRegister:
    invoices: list[Invoice] = field(default_factory=list)

    def add(self, invoice: Invoice) -> None:
        validate_invoice(invoice)
        key = (invoice.kind, invoice.party_id.casefold(), invoice.invoice_id.casefold())
        if any((i.kind, i.party_id.casefold(), i.invoice_id.casefold()) == key for i in self.invoices):
            raise ValueError("Possible duplicate invoice")
        self.invoices.append(invoice)

    def totals(self) -> dict[str, Decimal]:
        result = {"sales": Decimal("0.00"), "purchase": Decimal("0.00")}
        for i in self.invoices:
            result[i.kind.value] += i.gross_amount
        return result
