"""Map validated fictional invoices to controlled double-entry journals.

VAT values here are illustrative, not a determination of Irish tax treatment.
"""
from decimal import Decimal
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.invoices import Invoice, InvoiceKind, validate_invoice
from ledgerpoint.ledger import Entry

def invoice_journal_lines(invoice: Invoice) -> list[Entry]:
    validate_invoice(invoice)
    net, vat, gross = invoice.net_amount, invoice.vat_amount, invoice.gross_amount
    if invoice.kind == InvoiceKind.SALES:
        lines = [Entry("1100", debit=gross), Entry("4000", credit=net)]
        if vat:
            lines.append(Entry("2100", credit=vat))
    elif invoice.kind == InvoiceKind.PURCHASE:
        lines = [Entry("5000", debit=net)]
        if vat:
            lines.append(Entry("1200", debit=vat))
        lines.append(Entry("2000", credit=gross))
    else:
        raise ValueError("Unsupported invoice kind")
    return lines

def post_invoice(book: ControlledLedger, invoice: Invoice) -> None:
    """Post using an ID scoped by kind, party and invoice reference."""
    lines = invoice_journal_lines(invoice)
    journal_id = f"INV:{invoice.kind.value}:{invoice.party_id.casefold()}:{invoice.invoice_id.casefold()}"
    book.post(journal_id, invoice.issue_date,
              f"{invoice.kind.value.title()} invoice {invoice.invoice_id}", lines)
