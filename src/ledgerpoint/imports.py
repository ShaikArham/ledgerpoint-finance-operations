"""Strict CSV invoice intake for fictional records only."""
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from io import StringIO
from ledgerpoint.invoices import Invoice, InvoiceKind, InvoiceRegister

FIELDS = ("invoice_id", "kind", "party_id", "issue_date", "due_date",
          "net_amount", "vat_rate", "currency")

def import_invoices_csv(content: str) -> InvoiceRegister:
    reader = csv.DictReader(StringIO(content))
    if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)) or set(reader.fieldnames) != set(FIELDS):
        raise ValueError("CSV header must contain exactly the expected columns")
    register = InvoiceRegister()
    for line_number, row in enumerate(reader, start=2):
        try:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Incorrect column count")
            invoice = Invoice(
                invoice_id=row["invoice_id"].strip(),
                kind=InvoiceKind(row["kind"].strip()),
                party_id=row["party_id"].strip(),
                issue_date=date.fromisoformat(row["issue_date"].strip()),
                due_date=date.fromisoformat(row["due_date"].strip()),
                net_amount=Decimal(row["net_amount"].strip()),
                vat_rate=Decimal(row["vat_rate"].strip()),
                currency=row["currency"].strip(),
            )
            register.add(invoice)
        except (ValueError, InvalidOperation, TypeError) as exc:
            raise ValueError(f"CSV row {line_number}: {exc}") from exc
    return register
