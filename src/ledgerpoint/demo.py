"""Reproducible fictional finance-operations scenario."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from ledgerpoint.invoices import Invoice, InvoiceKind
from ledgerpoint.settlements import SettlementBook, Party
from ledgerpoint.reconciliation import BankTransaction, reconcile, ReconciliationItem
from ledgerpoint.reporting import ProfitAndLoss, BalanceSheet, profit_and_loss, balance_sheet
from ledgerpoint.management import MonthlyResult, monthly_result

D = Decimal

@dataclass(frozen=True)
class DemoResult:
    book: SettlementBook
    reconciliation: tuple[ReconciliationItem, ...]
    profit_and_loss: ProfitAndLoss
    balance_sheet: BalanceSheet
    october: MonthlyResult

def build_demo() -> DemoResult:
    """All parties and transactions are fictional; VAT rates illustrative."""
    book = SettlementBook()
    book.add_party(Party("C-001", "Harbour Design Studio", InvoiceKind.SALES))
    book.add_party(Party("S-001", "North Quay Supplies", InvoiceKind.PURCHASE))
    sale = Invoice("SALE-001", InvoiceKind.SALES, "C-001",
                   date(2026, 10, 5), date(2026, 11, 4), D("1000.00"), D("0.23"))
    purchase = Invoice("BILL-001", InvoiceKind.PURCHASE, "S-001",
                       date(2026, 10, 7), date(2026, 11, 6), D("300.00"), D("0.23"))
    book.add_invoice(sale)
    book.add_invoice(purchase)
    book.allocate("RCPT-001", book.key(sale), D("500.00"), date(2026, 10, 15))
    book.allocate("PMT-001", book.key(purchase), D("369.00"), date(2026, 10, 20))
    bank = [
        BankTransaction("RCPT-001", date(2026, 10, 15), D("500.00")),
        BankTransaction("PMT-001", date(2026, 10, 20), D("-369.00")),
        BankTransaction("UNKNOWN-001", date(2026, 10, 21), D("-12.00")),
    ]
    cutoff = date(2026, 10, 31)
    return DemoResult(book, tuple(reconcile(book, bank, cutoff)),
                      profit_and_loss(book.ledger, cutoff),
                      balance_sheet(book.ledger, cutoff),
                      monthly_result(book.ledger, "2026-10"))
