"""CSV exports of fictional accounting reports."""
import csv
from io import StringIO
from ledgerpoint.reporting import TrialBalanceRow
from ledgerpoint.reconciliation import ReconciliationItem

def _csv(header: list[str], rows: list[list[str]]) -> str:
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue()

def trial_balance_csv(rows: list[TrialBalanceRow]) -> str:
    return _csv(["account_code", "account_name", "debit_eur", "credit_eur"],
                [[r.code, r.name, str(r.debit), str(r.credit)] for r in rows])

def reconciliation_csv(items: list[ReconciliationItem] | tuple[ReconciliationItem, ...]) -> str:
    return _csv(["reference", "status", "ledger_amount_eur", "bank_amount_eur"],
                [[i.reference, i.status,
                  "" if i.ledger_amount is None else str(i.ledger_amount),
                  "" if i.bank_amount is None else str(i.bank_amount)]
                 for i in items])
