"""Fictional cash movement and trade working-capital reporting.

Cash flows use posted settlement allocations, not unmatched bank statement rows.
Trade working capital is receivables minus payables; it excludes cash, VAT
control balances and other non-trade assets or liabilities.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from ledgerpoint.invoices import InvoiceKind
from ledgerpoint.settlements import SettlementBook

ZERO = Decimal("0.00")

@dataclass(frozen=True)
class CashFlowReport:
    start: date
    end: date
    customer_receipts: Decimal
    supplier_payments: Decimal
    net_settlement_cash_flow: Decimal
    opening_bank_balance: Decimal
    closing_bank_balance: Decimal
    other_posted_bank_movements: Decimal

@dataclass(frozen=True)
class WorkingCapitalReport:
    as_of: date
    trade_receivables: Decimal
    trade_payables: Decimal
    net_trade_working_capital: Decimal
    bank_balance: Decimal
    overdue_receivables: Decimal
    overdue_payables: Decimal

def _bank_balance(book: SettlementBook, through: date) -> Decimal:
    return book.ledger.trial_balance(through=through)["1000"]

def cash_flow(book: SettlementBook, start: date, end: date) -> CashFlowReport:
    if start > end:
        raise ValueError("Start date cannot follow end date")
    from datetime import timedelta
    opening = _bank_balance(book, start - timedelta(days=1)) if start > date.min else ZERO
    closing = _bank_balance(book, end)
    allocations = [a for a in book.allocations if start <= a.paid_on <= end]
    receipts = sum((a.amount for a in allocations if a.invoice_key[0] == InvoiceKind.SALES), ZERO)
    payments = sum((a.amount for a in allocations if a.invoice_key[0] == InvoiceKind.PURCHASE), ZERO)
    net = receipts - payments
    # A separate residual makes non-settlement bank postings visible, not silently classified.
    other = closing - opening - net
    return CashFlowReport(start, end, receipts, payments, net, opening, closing, other)

def working_capital(book: SettlementBook, as_of: date) -> WorkingCapitalReport:
    receivables = payables = overdue_ar = overdue_ap = ZERO
    for key, invoice in book.invoices.items():
        if invoice.issue_date > as_of:
            continue
        outstanding = book.outstanding(key, as_of)
        if invoice.kind == InvoiceKind.SALES:
            receivables += outstanding
            if invoice.due_date < as_of:
                overdue_ar += outstanding
        else:
            payables += outstanding
            if invoice.due_date < as_of:
                overdue_ap += outstanding
    return WorkingCapitalReport(as_of, receivables, payables,
                                receivables - payables, _bank_balance(book, as_of),
                                overdue_ar, overdue_ap)
