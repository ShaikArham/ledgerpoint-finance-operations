from datetime import date
from decimal import Decimal
import pytest
from ledgerpoint.invoices import Invoice, InvoiceKind, InvoiceRegister, validate_invoice

D = Decimal

def sample(**overrides):
    args = dict(invoice_id="INV-001", kind=InvoiceKind.SALES, party_id="C001",
                issue_date=date(2026, 10, 1), due_date=date(2026, 10, 31),
                net_amount=D("100.00"), vat_rate=D("0.23"))
    args.update(overrides)
    return Invoice(**args)

def test_invoice_totals():
    i = sample()
    assert i.vat_amount == D("23.00")
    assert i.gross_amount == D("123.00")

def test_register_sales_and_purchase():
    r = InvoiceRegister()
    r.add(sample())
    r.add(sample(invoice_id="BILL-01", party_id="S001", kind=InvoiceKind.PURCHASE,
                 net_amount=D("50.00"), vat_rate=D("0")))
    assert r.totals() == {"sales": D("123.00"), "purchase": D("50.00")}

def test_duplicate_same_party_and_reference_rejected():
    r = InvoiceRegister()
    r.add(sample())
    with pytest.raises(ValueError, match="duplicate"):
        r.add(sample(invoice_id="inv-001", party_id="c001"))
    assert len(r.invoices) == 1

def test_same_reference_different_party_allowed():
    r = InvoiceRegister()
    r.add(sample())
    r.add(sample(party_id="C002"))
    assert len(r.invoices) == 2

def test_due_date_before_issue_rejected():
    with pytest.raises(ValueError, match="Due date"):
        validate_invoice(sample(due_date=date(2026, 9, 30)))

def test_negative_amount_rejected():
    with pytest.raises(ValueError, match="net amount"):
        validate_invoice(sample(net_amount=D("-1")))

def test_fractional_cent_rejected():
    with pytest.raises(ValueError, match="net amount"):
        validate_invoice(sample(net_amount=D("1.001")))

def test_currency_rejected():
    with pytest.raises(ValueError, match="EUR"):
        validate_invoice(sample(currency="USD"))

def test_invalid_vat_rate_rejected():
    with pytest.raises(ValueError, match="VAT"):
        validate_invoice(sample(vat_rate=D("1.1")))

def test_rounding_half_up():
    assert sample(net_amount=D("0.50"), vat_rate=D("0.01")).vat_amount == D("0.01")
