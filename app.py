"""LedgerPoint: fictional finance operations interactive demonstration."""
from datetime import date
from decimal import Decimal
import streamlit as st
from ledgerpoint.demo import build_demo
from ledgerpoint.reporting import trial_balance
from ledgerpoint.exports import trial_balance_csv, reconciliation_csv
from ledgerpoint.management import month_end_checks
from ledgerpoint.reconciliation import reconciliation_summary
from ledgerpoint.triage import investigate
from ledgerpoint.receivables import invoice_positions

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
    st.subheader("October 2026 · Executive overview")
    a, b, c, d = st.columns(4)
    a.metric("Revenue", f"€{demo.october.revenue:,.2f}")
    b.metric("Expenses", f"€{demo.october.expenses:,.2f}")
    c.metric("Net profit", f"€{demo.october.profit:,.2f}")
    exceptions = [item for item in demo.reconciliation if item.status != "matched"]
    d.metric("Bank exceptions", len(exceptions))

    st.markdown("#### Financial snapshot")
    left, right = st.columns(2)
    with left:
        st.bar_chart({"Revenue": float(demo.october.revenue),
                      "Expenses": float(demo.october.expenses),
                      "Net profit": float(demo.october.profit)})
        st.caption("October 2026 fictional profit-and-loss amounts in EUR.")
    with right:
        open_invoices = invoice_positions(book, date(2026, 10, 31))
        receivables = sum((p.outstanding for p in open_invoices if p.kind == "sales"), Decimal("0.00"))
        payables = sum((p.outstanding for p in open_invoices if p.kind == "purchase"), Decimal("0.00"))
        st.metric("Outstanding customer invoices", f"€{receivables:,.2f}")
        st.metric("Outstanding supplier invoices", f"€{payables:,.2f}")
        st.write(f"**Bank matching:** {len(demo.reconciliation) - len(exceptions)} of {len(demo.reconciliation)} references matched")

    st.markdown("#### Items needing attention")
    if exceptions:
        for item in exceptions:
            st.warning(f"{item.reference}: {item.status.replace('_', ' ').title()} — review in Bank reconciliation")
    else:
        st.success("No bank reconciliation exceptions.")
    st.markdown("#### Follow the workflow")
    st.write("Invoices → payment allocations → bank matching → financial reporting → close controls")
    st.caption("Figures reflect the fixed fictional October scenario. Charts are descriptive, not forecasts.")

    with st.expander("Start here: a 3-minute reviewer walkthrough", expanded=True):
        st.markdown("""
**1. Overview (30 seconds).** Review revenue, expenses, profit and the flagged bank exception.

**2. Invoices (45 seconds).** Find SALE-001, its €730 outstanding balance, and change the reporting date to see invoice ageing.

**3. Bank reconciliation (60 seconds).** Select UNKNOWN-001 and read why the €12 outgoing bank transaction remains unmatched. No ledger entry is created.

**4. Financial reports (30 seconds).** Review the simplified statements and download the trial balance.

**5. Controls (30 seconds).** Review the close-readiness checks and why the period remains open.

**What this demonstrates:** SQL/Python-style validation thinking, financial workflow modelling, exception handling and clear operational reporting. It does not represent professional accounting experience or a production accounting system.
""")

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
    st.dataframe(invoice_rows, width="stretch", hide_index=True)
    st.caption("Balances are computed from posted fictional invoices and payment allocations.")
    st.markdown("#### Invoice ageing and payment follow-up")
    as_of = st.date_input("Reporting date", value=date(2026, 10, 31),
                          min_value=date(2026, 10, 1), max_value=date(2027, 12, 31),
                          key="invoice_ageing_date")
    positions = invoice_positions(book, as_of)
    kinds = st.multiselect("Invoice type", ["sales", "purchase"], default=["sales", "purchase"],
                           format_func=lambda x: x.title(), key="ageing_types")
    filtered = [p for p in positions if p.kind in kinds]
    sales_due = sum((p.outstanding for p in filtered if p.kind == "sales"), Decimal("0.00"))
    purchase_due = sum((p.outstanding for p in filtered if p.kind == "purchase"), Decimal("0.00"))
    overdue = sum((p.outstanding for p in filtered if p.days_overdue > 0), Decimal("0.00"))
    x, y, z = st.columns(3)
    x.metric("Customer receivables", f"€{sales_due:,.2f}")
    y.metric("Supplier payables", f"€{purchase_due:,.2f}")
    z.metric("Overdue balance", f"€{overdue:,.2f}")
    st.dataframe([{
        "Invoice": p.reference, "Party": p.party, "Type": p.kind.title(),
        "Due date": p.due_date.isoformat(), "Outstanding (€)": float(p.outstanding),
        "Days overdue": p.days_overdue, "Ageing bucket": p.bucket,
        "Suggested follow-up": p.action,
    } for p in filtered], width="stretch", hide_index=True)
    if not filtered:
        st.info("No open invoices match the selected reporting date and type.")
    st.caption("Snapshot amounts include payments recorded on or before the selected date. Suggested follow-ups are illustrative, not actions taken.")

with tab3:
    st.subheader("Bank reconciliation")
    rows = [{
        "Reference": item.reference,
        "Result": item.status.replace("_", " ").title(),
        "Ledger amount (€)": None if item.ledger_amount is None else float(item.ledger_amount),
        "Bank amount (€)": None if item.bank_amount is None else float(item.bank_amount),
    } for item in demo.reconciliation]
    st.dataframe(rows, width="stretch", hide_index=True)
    counts = reconciliation_summary(list(demo.reconciliation))
    st.write(f"Matched: **{counts['matched']}** · Exceptions: **{len(rows) - counts['matched']}**")
    st.markdown("#### Investigate a transaction")
    references = [item.reference for item in demo.reconciliation]
    selected_reference = st.selectbox("Bank or ledger reference", references,
                                     index=references.index("UNKNOWN-001") if "UNKNOWN-001" in references else 0)
    selected_item = next(item for item in demo.reconciliation if item.reference == selected_reference)
    investigation = investigate(selected_item)
    st.write(f"**Status:** {investigation.status.replace('_', ' ').title()}")
    st.write(f"**Ledger amount:** {'Not found' if selected_item.ledger_amount is None else f'€{selected_item.ledger_amount:,.2f}'}")
    st.write(f"**Bank amount:** {'Not found' if selected_item.bank_amount is None else f'€{selected_item.bank_amount:,.2f}'}")
    st.write(investigation.explanation)
    if investigation.resolved:
        st.success(investigation.next_action)
    else:
        st.warning(investigation.next_action)
    st.caption("Read-only investigation. No journal is posted and no exception is automatically cleared.")
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
                 width="stretch", hide_index=True)
    st.download_button("Download trial balance CSV", trial_balance_csv(tb),
                       file_name="ledgerpoint-trial-balance.csv", mime="text/csv")

with tab5:
    st.subheader("Accounting control checks")
    checks = month_end_checks(book.ledger, "2026-10")
    st.markdown("#### October close readiness")
    passed = sum(check.passed for check in checks)
    st.progress(passed / len(checks), text=f"{passed} of {len(checks)} accounting checks passed")
    for check in checks:
        with st.expander(f"{'✅' if check.passed else '⚠️'} {check.name}", expanded=not check.passed):
            st.write(check.details)
            if check.name == "Period locked" and not check.passed:
                st.info("This sample period remains open intentionally. Locking it would require an authorised close action in the accounting engine, not a dashboard checkbox.")
    exceptions = [item for item in demo.reconciliation if item.status != "matched"]
    st.markdown("#### Operational review before close")
    if exceptions:
        st.warning(f"{len(exceptions)} bank reconciliation exception(s) require investigation before treating this sample as fully reconciled.")
        for item in exceptions:
            st.write(f"• **{item.reference}**: {item.status.replace('_', ' ').title()}")
    else:
        st.success("No bank reconciliation exceptions in the current sample.")
    st.caption("Read-only close readiness. This dashboard does not lock periods, clear exceptions, approve entries or perform a statutory month-end close.")
    st.markdown("#### Scope and limitations")
    st.write("In-memory demonstration only. No real bank integration, payroll submissions, user authentication, persistent audit database or statutory financial reporting.")
    st.markdown("[Review the project source and tests](https://github.com/ShaikArham/ledgerpoint-finance-operations)")
