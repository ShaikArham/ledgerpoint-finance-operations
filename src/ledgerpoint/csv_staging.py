"""Strict, read-only CSV staging for fictional invoice and bank imports.

No imported rows are posted to the accounting ledger.
"""
import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from ledgerpoint.invoices import Invoice, InvoiceKind, validate_invoice

MAX_BYTES = 1_000_000
MAX_ROWS = 2000
SCHEMAS = {
    "invoices": ("invoice_id", "kind", "party_id", "issue_date", "due_date", "net_amount", "vat_rate"),
    "bank": ("reference", "date", "amount"),
}

@dataclass(frozen=True)
class StagingResult:
    clean: tuple[dict[str, str], ...]
    errors: tuple[dict[str, str], ...]
    total_rows: int

def _money(raw: str, label: str, *, allow_negative: bool = False) -> Decimal:
    try:
        value = Decimal(raw.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"{label}: invalid decimal") from None
    if not value.is_finite() or value.as_tuple().exponent < -2:
        raise ValueError(f"{label}: must be finite with at most two decimal places")
    if not allow_negative and value <= 0:
        raise ValueError(f"{label}: must be positive")
    if allow_negative and value == 0:
        raise ValueError(f"{label}: must not be zero")
    return value

def stage_csv(data: bytes, kind: str) -> StagingResult:
    if kind not in SCHEMAS:
        raise ValueError("Unknown import type")
    if len(data) > MAX_BYTES:
        raise ValueError("File exceeds 1 MB limit")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("CSV must use UTF-8 encoding") from None
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        columns = reader.fieldnames
        if not columns or len(columns) != len(set(columns)) or any(not col for col in columns):
            raise ValueError("Missing or duplicate CSV column headings")
        missing = set(SCHEMAS[kind]) - set(columns)
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        clean, errors, seen = [], [], set()
        total = 0
        for line_number, row in enumerate(reader, start=2):
            total += 1
            if total > MAX_ROWS:
                raise ValueError("CSV exceeds 2,000 data rows")
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("Incorrect number of columns")
                item = {name: (row[name] or "").strip() for name in SCHEMAS[kind]}
                if kind == "invoices":
                    try:
                        invoice_kind = InvoiceKind(item["kind"].lower())
                    except ValueError:
                        raise ValueError("kind must be sales or purchase") from None
                    try:
                        net = _money(item["net_amount"], "net_amount")
                        rate = Decimal(item["vat_rate"])
                        invoice = Invoice(item["invoice_id"], invoice_kind, item["party_id"],
                                          date.fromisoformat(item["issue_date"]),
                                          date.fromisoformat(item["due_date"]), net, rate)
                        validate_invoice(invoice)
                    except (ValueError, InvalidOperation) as exc:
                        raise ValueError(str(exc)) from None
                    key = (invoice_kind.value, item["party_id"].casefold(), item["invoice_id"].casefold())
                    item["kind"] = invoice_kind.value
                    item["net_amount"] = str(net)
                    item["vat_rate"] = str(rate)
                else:
                    if not item["reference"]:
                        raise ValueError("Bank reference required")
                    date.fromisoformat(item["date"])
                    amount = _money(item["amount"], "amount", allow_negative=True)
                    key = item["reference"].casefold()
                    item["amount"] = str(amount)
                if key in seen:
                    raise ValueError("Duplicate reference in uploaded CSV")
                seen.add(key)
                clean.append(item)
            except ValueError as exc:
                errors.append({"row": str(line_number), "reason": str(exc)})
        return StagingResult(tuple(clean), tuple(errors), total)
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV: {exc}") from None

def csv_export(rows: tuple[dict[str, str], ...], columns: tuple[str, ...]) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()
