"""CSV staging rejects bad inputs and never posts to a ledger."""
import pytest
from ledgerpoint.csv_staging import stage_csv, csv_export, detect_csv_kind

HEADER = "invoice_id,kind,party_id,issue_date,due_date,net_amount,vat_rate\n"
GOOD = "A-1,sales,C-001,2026-10-05,2026-11-04,100.00,0.23\n"

def test_valid_invoice():
    result = stage_csv((HEADER + GOOD).encode(), "invoices")
    assert result.total_rows == 1
    assert len(result.clean) == 1
    assert result.errors == ()

def test_duplicate_invoice_rejected():
    result = stage_csv((HEADER + GOOD + GOOD).encode(), "invoices")
    assert len(result.clean) == 1
    assert len(result.errors) == 1
    assert "Duplicate" in result.errors[0]["reason"]

@pytest.mark.parametrize("row", [
    "A-1,sales,C-001,2026-10-05,2026-11-04,NaN,0.23",
    "A-1,sales,C-001,2026-10-05,2026-11-04,1.234,0.23",
    "A-1,other,C-001,2026-10-05,2026-11-04,100,0.23",
    "A-1,sales,C-001,2026-10-05,2026-10-04,100,0.23",
])
def test_invalid_invoice_rows(row):
    result = stage_csv((HEADER + row + "\n").encode(), "invoices")
    assert not result.clean
    assert len(result.errors) == 1

def test_bank_positive_and_negative():
    data = b"reference,date,amount\nR1,2026-10-01,500\nP1,2026-10-02,-12.50\n"
    result = stage_csv(data, "bank")
    assert len(result.clean) == 2

def test_bank_duplicate_casefold():
    data = b"reference,date,amount\nR1,2026-10-01,500\nr1,2026-10-02,100\n"
    assert len(stage_csv(data, "bank").errors) == 1

def test_missing_columns_rejected():
    with pytest.raises(ValueError, match="Missing columns"):
        stage_csv(b"reference,amount\nR1,2\n", "bank")

def test_duplicate_headings_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        stage_csv(b"reference,reference,date,amount\nR1,R2,2026-10-01,1\n", "bank")

def test_wrong_number_of_columns_rejected():
    result = stage_csv(b"reference,date,amount\nR1,2026-10-01,1,extra\n", "bank")
    assert len(result.errors) == 1

def test_invalid_encoding_rejected():
    with pytest.raises(ValueError, match="UTF-8"):
        stage_csv(b"\xff", "bank")

def test_oversized_file_rejected():
    with pytest.raises(ValueError, match="1 MB"):
        stage_csv(b"x" * 1000001, "bank")

def test_clean_csv_export():
    result = stage_csv(b"reference,date,amount\nR1,2026-10-01,5\n", "bank")
    assert "R1,2026-10-01,5" in csv_export(result.clean, ("reference", "date", "amount"))

def test_ledgerpoint_register_roundtrip():
    data = ("Invoice,Type,Party,Issue date,Due date,Net (€),Illustrative VAT (€),Gross (€),Outstanding (€),Status\\n"
            "SALE-001,Sales,Harbour Design Studio,2026-10-05,2026-11-04,1000,230,1230,730,Outstanding\\n"
            "BILL-001,Purchase,North Quay Supplies,2026-10-07,2026-11-06,300,69,369,0,Settled\\n").replace("\\n", "\n")
    result = stage_csv(data.encode("utf-8-sig"), "invoice_register")
    assert result.total_rows == 2
    assert len(result.clean) == 2
    assert result.errors == ()
    exported = csv_export(result.clean, ("Invoice", "Type", "Party", "Issue date", "Due date",
                                         "Net (€)", "Illustrative VAT (€)", "Gross (€)", "Outstanding (€)", "Status"))
    assert "Harbour Design Studio" in exported

def test_register_rejects_wrong_totals():
    data = ("Invoice,Type,Party,Issue date,Due date,Net (€),Illustrative VAT (€),Gross (€),Outstanding (€),Status\\n"
            "SALE-001,Sales,Harbour Design Studio,2026-10-05,2026-11-04,1000,230,1200,730,Outstanding\\n").replace("\\n", "\n")
    result = stage_csv(data.encode(), "invoice_register")
    assert len(result.errors) == 1
    assert "must equal gross" in result.errors[0]["reason"]

def test_auto_detect_invoice_intake():
    assert detect_csv_kind((HEADER + GOOD).encode()) == "invoices"
    assert len(stage_csv((HEADER + GOOD).encode(), "auto").clean) == 1

def test_auto_detect_bank():
    data = b"reference,date,amount\\nR1,2026-10-01,5\\n".replace(b"\\n", b"\n")
    assert detect_csv_kind(data) == "bank"

def test_auto_detect_invoice_register():
    data = ("Invoice,Type,Party,Issue date,Due date,Net (€),Illustrative VAT (€),Gross (€),Outstanding (€),Status\\n"
            "SALE-001,Sales,Harbour Design Studio,2026-10-05,2026-11-04,1000,230,1230,730,Outstanding\\n").replace("\\n", "\n").encode("utf-8-sig")
    assert detect_csv_kind(data) == "invoice_register"
    assert len(stage_csv(data, "auto").clean) == 1

def test_auto_detect_unknown_format():
    with pytest.raises(ValueError, match="Unrecognised"):
        stage_csv(b"foo,bar\\na,b\\n".replace(b"\\n", b"\n"), "auto")

def test_spreadsheet_formula_escaped_in_text_export():
    import csv
    import io
    rows = ({"reference": "=1+1", "date": "2026-10-01", "amount": "-12.50"},)
    output = csv_export(rows, ("reference", "date", "amount"))
    parsed = next(csv.DictReader(io.StringIO(output)))
    assert parsed["reference"] == "'=1+1"
    assert parsed["amount"] == "-12.50"

def test_register_negative_vat_rejected():
    header = ",".join(("Invoice","Type","Party","Issue date","Due date","Net (€)",
                       "Illustrative VAT (€)","Gross (€)","Outstanding (€)","Status"))
    row = "INV-1,Sales,Party,2026-10-01,2026-10-30,100,-1,99,0,Settled"
    result = stage_csv((header + "\n" + row + "\n").encode(), "invoice_register")
    assert not result.clean
    assert len(result.errors) == 1

def test_register_invalid_outstanding_is_row_error():
    header = ",".join(("Invoice","Type","Party","Issue date","Due date","Net (€)",
                       "Illustrative VAT (€)","Gross (€)","Outstanding (€)","Status"))
    row = "INV-1,Sales,Party,2026-10-01,2026-10-30,100,0,100,invalid,Outstanding"
    result = stage_csv((header + "\n" + row + "\n").encode(), "invoice_register")
    assert not result.clean
    assert len(result.errors) == 1
