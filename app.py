"""LedgerPoint: fictional finance operations interactive demonstration."""
from datetime import date
from decimal import Decimal
import streamlit as st
from ledgerpoint.demo import build_demo
from ledgerpoint.reporting import trial_balance
from ledgerpoint.exports import trial_balance_csv, reconciliation_csv
from ledgerpoint.management import month_end_checks
from ledgerpoint.reconciliation import reconciliation_summary

st.set_page_config(page_title="LedgerPoint | Finance Operations", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem}
h1, h2, h3 {letter-spacing: -.025em}
[data-testid="stMetric"] {background: #f3f6fa; border: 1px solid #e1e8f0; padding: 16px; border-radius: 12px}
</style>
""", unsafe_allow_html=True)
st.title("LedgerPoint")
st.caption("Finance Operations Simulator · Independent portfolio project · Fictional data only")
st.info("Educational demonstration. Not affiliated with DataPoint Ireland. VAT amounts are illustrative, not Irish tax advice.")

demo = build_demo()
book = demo.book
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Invoices", "Bank reconciliation", "Financial reports", "Controls"
])

with tab1:
    st.subheader("October 2026 financial overview")
    a, b, c, d = st.columns(4)
    a.metric("Revenue", f"€{demo.october.revenue:,.2f}")
    b.metric("Expenses", f"€{demo.october.expenses:,.2f}")
    c.metric("Net profit", f"€{demo.october.profit:,.2f}")
    d.metric("Reconciliation exceptions",
             sum(item.status != "matched" for item in demo.reconciliation))
    st.markdown("### How the workflow connects")
    st.write("Invoice validation → double-entry posting → payment allocation → bank matching → financial reporting")
    st.write("The demo includes a partially paid customer invoice, a settled supplier invoice and an unmatched bank transaction.")

with tab2:
    st.subheader("Sales and purchase invoice register")
    invoice_rows = []
    for key, invoice in book.invoices.items():
        outstanding = book.outstanding(key)
        invoice_rows.append({
            "Invoice": invoice.invoice_id,
            "Type": invoice.kind.value.title(),
            "Party": book.parties[(invoice.kind, invoice.party_id.casefold())].name,
            "Issue date": invoice.issue_date.isoformat(),
            "Due date": invoice.due_date.isoformat(),
            "Net (€)": float(invoice.net_amount),
            "Illustrative VAT (€)": float(invoice.vat_amount),
            "Gross (€)": float(invoice.gross_amount),
            "Outstanding (€)": float(outstanding),
            "Status": "Settled" if outstanding == 0 else "Outstanding",
        })
    st.dataframe(invoice_rows, use_container_width=True, hide_index=True)
    st.caption("Balances are computed from posted fictional invoices and payment allocations.")

with tab3:
    st.subheader("Bank reconciliation")
    rows = [{
        "Reference": item.reference,
        "Result": item.status.replace("_", " ").title(),
        "Ledger amount (€)": None if item.ledger_amount is None else float(item.ledger_amount),
        "Bank amount (€)": None if item.bank_amount is None else float(item.bank_amount),
    } for item in demo.reconciliation]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    counts = reconciliation_summary(list(demo.reconciliation))
    st.write(f"Matched: **{counts['matched']}** · Exceptions: **{len(rows) - counts['matched']}**")
    st.warning("UNKNOWN-001 is a bank-only transaction. Investigate it before treating the bank statement as fully reconciled.")
    st.download_button("Download reconciliation CSV",
                       reconciliation_csv(demo.reconciliation),
                       file_name="ledgerpoint-reconciliation.csv", mime="text/csv")

with tab4:
    st.subheader("Financial statements")
    pnl = demo.profit_and_loss
    balance = demo.balance_sheet
    left, right = st.columns(2)
    with left:
        st.markdown("#### Profit and loss")
        st.write(f"Revenue: **€{pnl.revenue:,.2f}**")
        st.write(f"Expenses: **€{pnl.expenses:,.2f}**")
        st.write(f"Net profit: **€{pnl.net_profit:,.2f}**")
    with right:
        st.markdown("#### Simplified balance sheet")
        st.write(f"Assets: **€{balance.assets:,.2f}**")
        st.write(f"Liabilities: **€{balance.liabilities:,.2f}**")
        st.write(f"Total equity: **€{balance.total_equity:,.2f}**")
        st.write(f"Balanced: **{'Yes' if balance.balanced else 'No'}**")
    st.markdown("#### Trial balance")
    tb = trial_balance(book.ledger)
    st.dataframe([{"Account": r.code, "Name": r.name, "Debit (€)": float(r.debit),
                   "Credit (€)": float(r.credit)} for r in tb],
                 use_container_width=True, hide_index=True)
    st.download_button("Download trial balance CSV", trial_balance_csv(tb),
                       file_name="ledgerpoint-trial-balance.csv", mime="text/csv")

with tab5:
    st.subheader("Accounting control checks")
    checks = month_end_checks(book.ledger, "2026-10")
    for check in checks:
        st.write(f"{'✅' if check.passed else '⚪'} **{check.name}**: {check.details}")
    st.caption("An unlocked period is expected in this demonstration. These checks are not a statutory month-end close.")
    st.markdown("#### Scope and limitations")
    st.write("In-memory demonstration only. No real bank integration, payroll submissions, user authentication, persistent audit database or statutory financial reporting.")
    st.markdown("[Review the project source and tests](https://github.com/ShaikArham/ledgerpoint-finance-operations)")
