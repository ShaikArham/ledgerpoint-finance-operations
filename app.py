"""LedgerPoint: fictional finance operations interactive demonstration."""
from datetime import date
from copy import deepcopy
from decimal import Decimal
import streamlit as st
from ledgerpoint.demo import build_demo
from ledgerpoint.reporting import trial_balance
from ledgerpoint.exports import trial_balance_csv, reconciliation_csv
from ledgerpoint.management import month_end_checks
from ledgerpoint.reconciliation import reconciliation_summary
from ledgerpoint.triage import investigate
from ledgerpoint.receivables import invoice_positions
from ledgerpoint.manual_entry import post_manual
from ledgerpoint.csv_staging import stage_csv, csv_export, SCHEMAS, detect_csv_kind

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview", "Invoices", "Bank reconciliation", "Financial reports", "Controls", "Journal sandbox", "CSV staging"
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
        st.bar_chart([
            {"Category": "Revenue", "EUR": float(demo.october.revenue)},
            {"Category": "Expenses", "EUR": float(demo.october.expenses)},
            {"Category": "Net profit", "EUR": float(demo.october.profit)},
        ], x="Category", y="EUR")
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

with tab6:
    st.subheader("Manual journal sandbox")
    st.info("Practice-only entries in your current browser session. This sandbox is separate from the baseline invoice, bank reconciliation and financial reports. No changes are saved to a database.")
    if "manual_sandbox" not in st.session_state:
        st.session_state.manual_sandbox = deepcopy(book.ledger)
    sandbox = st.session_state.manual_sandbox
    accounts = list(sandbox.accounts)
    def account_label(code):
        return f"{code} · {sandbox.accounts[code].name}"
    with st.form("manual_journal_form", clear_on_submit=False):
        journal_id = st.text_input("Unique journal ID", value="MAN-001")
        posting_date = st.date_input("Posting date", value=date(2026, 10, 22), key="manual_post_date")
        description = st.text_input("Description", value="Fictional bank charge adjustment")
        debit_account = st.selectbox("Debit account", accounts, index=accounts.index("5000"),
                                     format_func=account_label)
        credit_account = st.selectbox("Credit account", accounts, index=accounts.index("1000"),
                                      format_func=account_label)
        amount = st.text_input("Amount (EUR)", value="12.00")
        submitted = st.form_submit_button("Validate and post to sandbox")
    if submitted:
        try:
            post_manual(sandbox, journal_id, posting_date, description,
                        debit_account, credit_account, amount)
        except (ValueError, TypeError) as exc:
            st.error(f"Not posted: {exc}")
        else:
            st.success(f"Journal {journal_id.strip()} posted to this session's sandbox.")
    st.markdown("#### Sandbox journal history")
    sandbox_journals = [j for j in sandbox.history if j.journal_id.startswith("MAN-")]
    st.dataframe([{
        "Journal": j.journal_id, "Date": j.posting_date.isoformat(),
        "Description": j.description,
        "Debit": f"{j.entries[0].account} · €{j.entries[0].debit:,.2f}",
        "Credit": f"{j.entries[1].account} · €{j.entries[1].credit:,.2f}",
    } for j in sandbox_journals], width="stretch", hide_index=True)
    st.markdown("#### Sandbox trial balance")
    balances = sandbox.trial_balance()
    st.dataframe([{
        "Account": account_label(code),
        "Debit (€)": float(max(value, Decimal("0.00"))),
        "Credit (€)": float(max(-value, Decimal("0.00"))),
    } for code, value in balances.items() if value != 0], width="stretch", hide_index=True)
    st.caption("The sandbox includes the fictional baseline journals plus any manual entries made during this session.")
    if st.button("Reset sandbox to baseline", key="reset_manual_sandbox"):
        st.session_state.manual_sandbox = deepcopy(book.ledger)
        st.rerun()

with tab7:
    st.subheader("CSV upload and quality checks")
    st.info("Upload fictional data for validation only. Nothing is posted to the ledger or sent to a bank.")
    import_type = st.radio("Import type", ["auto", "invoices", "bank", "invoice_register"], horizontal=True,
                           format_func=lambda value: {"auto": "Auto-detect (recommended)", "invoices": "Invoice intake", "bank": "Bank transactions", "invoice_register": "LedgerPoint invoice register export"}[value])
    columns = SCHEMAS.get(import_type)
    if columns:
        st.caption("Required columns: " + ", ".join(columns))
    else:
        st.caption("Upload any supported CSV format. LedgerPoint identifies its column structure automatically.")
    st.caption("Choose LedgerPoint invoice register export for CSVs downloaded from the invoice table. Party names are preserved; no party IDs are invented.")
    sample = (
        "invoice_id,kind,party_id,issue_date,due_date,net_amount,vat_rate\\n"
        "DEMO-001,sales,C-001,2026-10-05,2026-11-04,100.00,0.23\\n"
        "DEMO-001,sales,C-001,2026-10-05,2026-11-04,100.00,0.23\\n"
        if import_type in ("invoices", "auto") else
        "reference,date,amount\\nBANK-001,2026-10-15,500.00\\n"
        "BANK-001,2026-10-16,500.00\\n"
        if import_type == "bank" else
        "Invoice,Type,Party,Issue date,Due date,Net (€),Illustrative VAT (€),Gross (€),Outstanding (€),Status\\n"
        "SALE-001,Sales,Harbour Design Studio,2026-10-05,2026-11-04,1000,230,1230,730,Outstanding\\n"
        "BILL-001,Purchase,North Quay Supplies,2026-10-07,2026-11-06,300,69,369,0,Settled\\n"
    ).replace("\\n", "\n")
    st.download_button("Download sample CSV", sample, file_name=f"ledgerpoint-{import_type}-sample.csv",
                       mime="text/csv", key=f"sample_{import_type}")
    upload = st.file_uploader("Choose a UTF-8 CSV file (maximum 1 MB, 2,000 rows)",
                              type=["csv"], key=f"staging_{import_type}")
    if upload is not None:
        try:
            detected_type = detect_csv_kind(upload.getvalue()) if import_type == "auto" else import_type
            result = stage_csv(upload.getvalue(), detected_type)
        except ValueError as exc:
            st.error(f"Import rejected: {exc}")
        else:
            st.success("Detected format: " + {"invoices": "Invoice intake", "bank": "Bank transactions", "invoice_register": "LedgerPoint invoice register export"}[detected_type])
            export_columns = SCHEMAS[detected_type]
            one, two, three = st.columns(3)
            one.metric("Rows examined", result.total_rows)
            two.metric("Valid rows", len(result.clean))
            three.metric("Rejected rows", len(result.errors))
            if result.clean:
                st.markdown("#### Validated preview")
                st.dataframe(list(result.clean), width="stretch", hide_index=True)
                st.download_button("Download cleaned CSV", csv_export(result.clean, export_columns),
                                   file_name=f"ledgerpoint-{detected_type}-clean.csv",
                                   mime="text/csv", key=f"clean_{import_type}")
            if result.errors:
                st.markdown("#### Rows needing correction")
                st.dataframe(list(result.errors), width="stretch", hide_index=True)
                st.download_button("Download error report", csv_export(result.errors, ("row", "reason")),
                                   file_name=f"ledgerpoint-{import_type}-errors.csv",
                                   mime="text/csv", key=f"errors_{import_type}")
            if not result.errors:
                st.success("All uploaded rows passed staging validation.")
    st.caption("Staging detects duplicates within the uploaded file only. It does not compare against existing ledger records or verify bank authenticity.")
