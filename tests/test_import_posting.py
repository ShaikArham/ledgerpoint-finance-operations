from datetime import date
from decimal import Decimal
import pytest
from ledgerpoint.accounts import Account, AccountType
from ledgerpoint.controlled import ControlledLedger
from ledgerpoint.imports import import_invoices_csv
from ledgerpoint.invoices import Invoice, InvoiceKind
from ledgerpoint.posting import post_invoice

D = Decimal
HEADER = "invoice_id,kind,party_id,issue_date,due_date,net_amount,vat_rate,currency\n"
ROW = "INV-001,sales,C001,2026-10-01,2026-10-31,100.00,0.23,EUR\n"

def invoice(kind=InvoiceKind.SALES, vat=D("0.23")):
    return Invoice("INV-001", kind, "C001", date(2026,10,1),
                   date(2026,10,31), D("100.00"), vat)

def test_import_valid_csv():
    register = import_invoices_csv(HEADER + ROW)
    assert len(register.invoices) == 1
    assert register.invoices[0].gross_amount == D("123.00")

def test_import_duplicate_rejected():
    with pytest.raises(ValueError, match="row 3"):
        import_invoices_csv(HEADER + ROW + ROW)

def test_import_missing_column_rejected():
    with pytest.raises(ValueError, match="header"):
        import_invoices_csv("invoice_id,kind\nINV-1,sales\n")

def test_import_invalid_date_rejected():
    with pytest.raises(ValueError, match="row 2"):
        import_invoices_csv(HEADER + ROW.replace("2026-10-31", "2026-99-31"))

def test_import_extra_column_rejected():
    with pytest.raises(ValueError, match="row 2"):
        import_invoices_csv(HEADER + ROW.strip() + ",EXTRA\n")

def test_sales_invoice_posting():
    book = ControlledLedger()
    post_invoice(book, invoice())
    b = book.trial_balance()
    assert b["1100"] == D("123")
    assert b["4000"] == D("-100")
    assert b["2100"] == D("-23")
    assert sum(b.values()) == 0

def test_purchase_invoice_posting():
    book = ControlledLedger()
    book.accounts["1200"] = Account("1200", "Input VAT", AccountType.ASSET)
    post_invoice(book, invoice(InvoiceKind.PURCHASE))
    b = book.trial_balance()
    assert b["5000"] == D("100")
    assert b["1200"] == D("23")
    assert b["2000"] == D("-123")
    assert sum(b.values()) == 0

def test_zero_vat_invoice_posting():
    book = ControlledLedger()
    post_invoice(book, invoice(vat=D("0")))
    assert len(book.history[0].entries) == 2
    assert sum(book.trial_balance().values()) == 0

def test_double_post_rejected():
    book = ControlledLedger()
    post_invoice(book, invoice())
    with pytest.raises(ValueError, match="already used"):
        post_invoice(book, invoice())
    assert len(book.history) == 1

def test_closed_period_rejected():
    book = ControlledLedger()
    book.close_period("2026-10")
    with pytest.raises(ValueError, match="closed"):
        post_invoice(book, invoice())
    assert not book.history
