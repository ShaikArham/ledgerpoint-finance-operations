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
    "invoice_register": ("Invoice", "Type", "Party", "Issue date", "Due date", "Net (€)", "Illustrative VAT (€)", "Gross (€)", "Outstanding (€)", "Status"),
}

@dataclass(frozen=True)
class StagingResult:
    clean: tuple[dict[str, str], ...]
    errors: tuple[dict[str, str], ...]
    total_rows: int

def _money(raw: str, label: str, *, allow_negative: bool = False, allow_zero: bool = False) -> Decimal:
    try:
        value = Decimal(raw.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"{label}: invalid decimal") from None
    if not value.is_finite() or value.as_tuple().exponent < -2:
        raise ValueError(f"{label}: must be finite with at most two decimal places")
    if not allow_negative and (value < 0 or (value == 0 and not allow_zero)):
        raise ValueError(f"{label}: must be positive")
    if allow_negative and value == 0:
        raise ValueError(f"{label}: must not be zero")
    return value

def detect_csv_kind(data: bytes) -> str:
    """Recognise supported CSV headers without guessing missing accounting fields."""
    if len(data) > MAX_BYTES:
        raise ValueError("File exceeds 1 MB limit")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("CSV must use UTF-8 encoding") from None
    try:
        header = next(csv.reader(io.StringIO(text, newline=""), strict=True), None)
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV: {exc}") from None
    if not header or len(header) != len(set(header)) or any(not name for name in header):
        raise ValueError("Missing or duplicate CSV column headings")
    matches = [kind for kind, required in SCHEMAS.items() if set(required).issubset(header)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError("Ambiguous CSV format; select a specific import type")
    raise ValueError("Unrecognised CSV columns. Supported formats: invoice intake, bank transactions, LedgerPoint invoice register export")

def stage_csv(data: bytes, kind: str) -> StagingResult:
    if kind == "auto":
        kind = detect_csv_kind(data)
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
                if kind == "invoice_register":
                    if not item["Invoice"] or not item["Party"]:
                        raise ValueError("Invoice and Party are required")
                    if item["Type"].casefold() not in ("sales", "purchase"):
                        raise ValueError("Type must be Sales or Purchase")
                    issued = date.fromisoformat(item["Issue date"])
                    due = date.fromisoformat(item["Due date"])
                    if due < issued:
                        raise ValueError("Due date precedes issue date")
                    net = _money(item["Net (€)"], "Net (€)")
                    vat = _money(item["Illustrative VAT (€)"], "Illustrative VAT (€)", allow_zero=True)
                    if vat < 0:
                        raise ValueError("Illustrative VAT cannot be negative")
                    gross = _money(item["Gross (€)"], "Gross (€)")
                    outstanding = _money(item["Outstanding (€)"], "Outstanding (€)", allow_zero=True)
                    if not outstanding.is_finite() or outstanding < 0 or outstanding > gross or outstanding.as_tuple().exponent < -2:
                        raise ValueError("Outstanding must be between zero and gross with at most two decimals")
                    if net + vat != gross:
                        raise ValueError("Net plus illustrative VAT must equal gross")
                    if item["Status"].casefold() not in ("settled", "outstanding"):
                        raise ValueError("Status must be Settled or Outstanding")
                    if (outstanding == 0) != (item["Status"].casefold() == "settled"):
                        raise ValueError("Status disagrees with outstanding balance")
                    key = (item["Type"].casefold(), item["Party"].casefold(), item["Invoice"].casefold())
                elif kind == "invoices":
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
    for row in rows:
        safe = {}
        for column in columns:
            value = str(row.get(column, ""))
            # Guard spreadsheet text fields; signed numeric bank amounts remain intact.
            if column not in ("amount", "net_amount", "vat_rate",
                              "Net (€)", "Illustrative VAT (€)", "Gross (€)",
                              "Outstanding (€)") and value.lstrip().startswith(
                                  ("=", "+", "-", "@", "\t", "\r", "\n")
                              ):
                value = "'" + value
            safe[column] = value
        writer.writerow(safe)
    return out.getvalue()
