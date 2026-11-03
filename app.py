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
from ledgerpoint.cases import create_case, update_case, STATUSES, PRIORITIES
from ledgerpoint.budget import parse_budget, compare_budget, forecast
from ledgerpoint.cashflow import cash_flow, working_capital
from ledgerpoint.payroll import PayrollInput, calculate_payroll, money
from ledgerpoint.approvals import ApprovalRegister, request_approval, review_approval

st.set_page_config(page_title="LedgerPoint | Finance Operations", page_icon="📊", layout="wide")
st.markdown("""
<style>
:root {--dp-ink:#183447;--dp-teal:#147f84}
.block-container {max-width: 1220px; padding-top: 1.4rem}
h1,h2,h3 {letter-spacing:-.035em;color:var(--dp-ink)}
[data-testid="stMetric"] {background:#f0f8f7;border:1px solid #d5e8e5;padding:16px;border-radius:14px;min-width:0}
[data-testid="stMetricValue"] {color:var(--dp-ink)}
[data-baseweb="tab-list"] {overflow-x:auto;scrollbar-width:thin}
[data-baseweb="tab"] {white-space:nowrap;flex-shrink:0}
.dp-hero {background:linear-gradient(115deg,#183447,#176e74);padding:26px;border-radius:18px;color:#fff;margin:6px 0 18px}
.dp-hero h2 {color:#fff!important;margin:8px 0;font-size:1.65rem}
.dp-hero p {color:#e5f3f1;line-height:1.6;margin:0}
.dp-hero small {display:block;color:#c9e7e4;margin-top:12px}
.dp-kicker {text-transform:uppercase;letter-spacing:.12em;color:#b9e8df;font-size:.75rem;font-weight:700}
@media(max-width:640px){.block-container{padding:1rem .7rem 2rem;max-width:100%}[data-testid="stMetric"]{padding:10px}.dp-hero{padding:18px;border-radius:14px}.dp-hero h2{font-size:1.3rem}}
</style>
""", unsafe_allow_html=True)
st.title("LedgerPoint")
st.markdown("""<div class="dp-hero"><div class="dp-kicker">Connect the dots · Finance operations</div><h2>From transactions to better decisions</h2><p>Explore management reporting, bank reconciliation, cash flow and operational exceptions through a fictional business case.</p><small>Independent portfolio concept inspired by DataPoint Ireland’s published services. Not commissioned or endorsed.</small></div>""", unsafe_allow_html=True)
st.caption("From invoice to insight · Interactive fictional finance-operations case study")
st.info("Independent portfolio demonstration using fictional data. Not affiliated with DataPoint Ireland. VAT and payroll figures are illustrative, not tax or payroll advice.")
st.markdown("**The case:** A fictional €12 bank debit has no matching ledger entry. Trace it from the executive dashboard through reconciliation, investigation and a maker-checker review, without inventing an accounting posting.")
st.caption("REVIEWER ROUTE · Overview → Bank reconciliation → Exception cases → Approvals & audit → Financial reports · ~3 minutes")

demo = build_demo()
book = demo.book
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "Overview", "Invoices", "Bank reconciliation", "Financial reports", "Controls", "Journal sandbox", "CSV staging", "Exception cases", "Budget & forecast", "Cash flow", "Payroll demo", "Approvals & audit"
])

with tab1:
    st.subheader("Business performance · October 2026")
    st.caption("01 / 05 · Establish the financial position and identify the exception requiring attention.")
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

    st.markdown("#### Priority investigation")
    if exceptions:
        for item in exceptions:
            st.warning(f"{item.reference}: {item.status.replace('_', ' ').title()} — review in Bank reconciliation")
    else:
        st.success("No bank reconciliation exceptions.")
    st.markdown("#### What happens next")
    st.write("**1. Reconcile:** identify the bank-only €12 entry.  **2. Investigate:** record an exception case.  **3. Review:** demonstrate a separate maker/checker decision.  **4. Report:** leave the ledger unchanged until supported evidence exists.")
    st.caption("Figures reflect the fixed fictional October scenario. Charts are descriptive, not forecasts.")

    with st.expander("Optional: detailed 3-minute reviewer walkthrough", expanded=False):
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
    st.caption("02 / 05 · Match bank references to posted settlements. Unmatched entries remain exceptions, not automatic journals.")
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
    st.caption("05 / 05 · Reconcile the financial story back to posted journals and the trial balance.")
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

with tab8:
    st.subheader("Exception case management")
    st.caption("03 / 05 · Track investigation decisions without altering financial balances.")
    st.info("Fictional, session-only case tracking. Marking a case resolved does not post accounting entries or change bank reconciliation.")
    if "exception_cases" not in st.session_state:
        st.session_state.exception_cases = {
            f"CASE-{i:03d}": create_case(f"CASE-{i:03d}", item.reference, item.status)
            for i, item in enumerate((x for x in demo.reconciliation if x.status != "matched"), start=1)
        }
    cases = st.session_state.exception_cases
    st.metric("Unresolved cases", sum(case.status != "Resolved" for case in cases.values()))
    if cases:
        st.dataframe([{"Case": case.case_id, "Reference": case.reference,
                       "Exception": case.exception_type, "Priority": case.priority,
                       "Status": case.status, "Owner": case.owner}
                      for case in cases.values()], width="stretch", hide_index=True)
        case_id = st.selectbox("Select case", list(cases))
        case = cases[case_id]
        with st.form("case_update"):
            status = st.selectbox("Case status", STATUSES, index=STATUSES.index(case.status))
            priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(case.priority))
            owner = st.text_input("Owner", value=case.owner)
            note = st.text_area("Investigation note", placeholder="Describe the evidence checked and next action")
            resolution = st.text_area("Resolution evidence (required when resolving)", value=case.resolution)
            submitted = st.form_submit_button("Save case update")
        if submitted:
            try:
                cases[case_id] = update_case(case, status=status, priority=priority,
                                             owner=owner, note=note, resolution=resolution)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Case updated in this session. Ledger and reconciliation unchanged.")
                st.rerun()
        st.markdown("#### Case activity history")
        if case.history:
            st.dataframe([{"Date": event.when, "Action": event.action, "Note": event.note}
                          for event in case.history], width="stretch", hide_index=True)
        else:
            st.caption("No case updates recorded yet.")
        if st.button("Reset fictional cases", key="reset_exception_cases"):
            del st.session_state.exception_cases
            st.rerun()
    else:
        st.success("No reconciliation exceptions in the fictional baseline.")

with tab9:
    st.subheader("Budget versus actual · October 2026")
    st.caption("Illustrative management budget. Actuals come from fictional posted journals; budgets and scenarios do not change the ledger.")
    with st.form("budget_comparison"):
        revenue_input = st.text_input("Budgeted revenue (€)", value="1200.00")
        expense_input = st.text_input("Budgeted expenses (€)", value="250.00")
        compare = st.form_submit_button("Calculate budget variances")
    if compare:
        try:
            st.session_state.budget_values = (parse_budget(revenue_input), parse_budget(expense_input))
        except ValueError as exc:
            st.error(str(exc))
    if "budget_values" in st.session_state:
        budget = compare_budget(demo.october, *st.session_state.budget_values)
        st.dataframe([
            {"Metric": "Revenue", "Actual (€)": float(budget.revenue_actual),
             "Budget (€)": float(budget.revenue_budget), "Variance (€)": float(budget.revenue_variance)},
            {"Metric": "Expenses", "Actual (€)": float(budget.expense_actual),
             "Budget (€)": float(budget.expense_budget), "Variance (€)": float(budget.expense_variance)},
            {"Metric": "Profit", "Actual (€)": float(budget.profit_actual),
             "Budget (€)": float(budget.profit_budget), "Variance (€)": float(budget.profit_variance)},
        ], width="stretch", hide_index=True)
        st.caption("Variance = actual minus budget. Positive expense variance means overspending; positive revenue/profit variance means above budget.")
    st.markdown("#### Scenario forecast")
    revenue_change = st.slider("Revenue change (%)", -100, 200, 10, key="forecast_revenue")
    expense_change = st.slider("Expense change (%)", -100, 200, 20, key="forecast_expense")
    scenario = forecast(demo.october, revenue_change, expense_change)
    a, b, c = st.columns(3)
    a.metric("Scenario revenue", f"€{scenario.revenue:,.2f}")
    b.metric("Scenario expenses", f"€{scenario.expenses:,.2f}")
    c.metric("Scenario profit", f"€{scenario.profit:,.2f}", delta=f"€{scenario.profit - demo.october.profit:+,.2f} vs actual")
    st.caption("A simple percentage what-if model, not a predictive statistical forecast or financial advice.")

with tab10:
    st.subheader("Cash flow and working capital")
    st.caption("Posted ledger cash movements and trade invoice balances only. Unmatched bank statement items are not assumed to be posted cash.")
    flow_start = st.date_input("Cash flow period start", value=date(2026, 10, 1), key="cash_start")
    flow_end = st.date_input("Cash flow period end", value=date(2026, 10, 31), key="cash_end")
    if flow_start > flow_end:
        st.error("Start date cannot follow end date")
    else:
        flow = cash_flow(book, flow_start, flow_end)
        a, b, c = st.columns(3)
        a.metric("Customer receipts", f"€{flow.customer_receipts:,.2f}")
        b.metric("Supplier payments", f"€{flow.supplier_payments:,.2f}")
        c.metric("Net settlement cash flow", f"€{flow.net_settlement_cash_flow:,.2f}")
        st.dataframe([
            {"Movement": "Opening posted bank balance", "EUR": float(flow.opening_bank_balance)},
            {"Movement": "Customer receipts", "EUR": float(flow.customer_receipts)},
            {"Movement": "Supplier payments", "EUR": -float(flow.supplier_payments)},
            {"Movement": "Other posted bank movements", "EUR": float(flow.other_posted_bank_movements)},
            {"Movement": "Closing posted bank balance", "EUR": float(flow.closing_bank_balance)},
        ], width="stretch", hide_index=True)
        st.caption("Other posted bank movements reconcile opening and closing balances; they are not automatically classified as operating cash flow.")
    st.markdown("#### Trade working capital")
    working_date = st.date_input("Working capital as of", value=date(2026, 10, 31), key="working_date")
    wc = working_capital(book, working_date)
    a, b, c = st.columns(3)
    a.metric("Trade receivables", f"€{wc.trade_receivables:,.2f}")
    b.metric("Trade payables", f"€{wc.trade_payables:,.2f}")
    c.metric("Net trade working capital", f"€{wc.net_trade_working_capital:,.2f}")
    st.write(f"**Posted bank balance:** €{wc.bank_balance:,.2f}")
    st.write(f"**Overdue customer balances:** €{wc.overdue_receivables:,.2f}")
    st.write(f"**Overdue supplier balances:** €{wc.overdue_payables:,.2f}")
    st.caption("Net trade working capital = trade receivables minus trade payables. This is not a statutory cash flow statement or a complete working-capital measure.")

with tab11:
    st.subheader("Illustrative payroll operations")
    st.warning("Training simulation only. The deduction percentage below is a fictional assumption, NOT Irish PAYE, USC, PRSI, pension, tax credits, or a Revenue-approved payroll calculation. Do not use for real payslips.")
    with st.form("illustrative_payroll"):
        employee_id = st.text_input("Fictional employee reference", value="DEMO-EMP-001")
        hours_text = st.text_input("Hours worked", value="40.00")
        hourly_text = st.text_input("Hourly pay (€)", value="20.00")
        deduction_text = st.text_input("Illustrative deduction assumption (%)", value="15.00")
        submitted = st.form_submit_button("Calculate illustrative payslip")
    if submitted:
        try:
            entry = PayrollInput(
                employee_id, money(hours_text, "Hours", maximum=Decimal("744")),
                money(hourly_text, "Hourly pay", maximum=Decimal("10000")),
                money(deduction_text, "Deduction percentage", maximum=Decimal("100")))
            st.session_state.illustrative_payslip = calculate_payroll(entry)
        except ValueError as exc:
            st.error(str(exc))
            st.session_state.pop("illustrative_payslip", None)
    if "illustrative_payslip" in st.session_state:
        slip = st.session_state.illustrative_payslip
        a, b, c = st.columns(3)
        a.metric("Gross pay", f"€{slip.gross:,.2f}")
        b.metric("Illustrative deduction", f"€{slip.illustrative_deduction:,.2f}")
        c.metric("Illustrative net pay", f"€{slip.net:,.2f}")
        st.caption(f"Fictional employee: {slip.employee_id}. No payroll records, tax returns or ledger entries are created.")
    st.markdown("#### Operational controls demonstrated")
    st.write("Input validation, decimal rounding, employee-reference checks, gross-to-net reconciliation and clear separation of hypothetical deductions from statutory payroll.")

with tab12:
    st.subheader("Approvals and operational audit history")
    st.caption("04 / 05 · Demonstrate a fictional maker-checker review and trace its session events.")
    st.warning("Fictional maker-checker demonstration only. User-entered actor names are not authenticated. Records are session-only, not tamper-proof, and decisions do not post to the ledger.")
    if "approval_register" not in st.session_state:
        st.session_state.approval_register = ApprovalRegister()
    register = st.session_state.approval_register
    st.metric("Pending approval requests", sum(r.status == "Pending" for r in register.requests))
    with st.form("new_approval_request"):
        request_id = st.text_input("Approval request ID", value="APR-001")
        reference = st.text_input("Transaction or case reference", value="UNKNOWN-001")
        requester = st.text_input("Requested by (fictional actor)", value="Demo maker")
        reason = st.text_area("Request reason", value="Investigate unmatched bank transaction")
        request_submitted = st.form_submit_button("Submit approval request")
    if request_submitted:
        try:
            st.session_state.approval_register = request_approval(
                register, request_id=request_id, reference=reference,
                actor=requester, reason=reason)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success("Approval request added to this session.")
            st.rerun()
    register = st.session_state.approval_register
    if register.requests:
        st.markdown("#### Approval register")
        st.dataframe([
            {"Request": r.request_id, "Reference": r.reference,
             "Requested by": r.requested_by, "Status": r.status,
             "Reviewed by": r.reviewed_by, "Review note": r.review_note}
            for r in register.requests
        ], width="stretch", hide_index=True)
        pending = [r.request_id for r in register.requests if r.status == "Pending"]
        if pending:
            with st.form("review_approval"):
                selected_request = st.selectbox("Pending request", pending)
                reviewer = st.text_input("Reviewed by (fictional actor)", value="Demo checker")
                decision = st.radio("Decision", ("Approved", "Rejected"), horizontal=True)
                review_note = st.text_area("Review evidence / explanation")
                review_submitted = st.form_submit_button("Record decision")
            if review_submitted:
                try:
                    st.session_state.approval_register = review_approval(
                        register, request_id=selected_request, actor=reviewer,
                        decision=decision, note=review_note)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.success("Decision recorded in the session activity history.")
                    st.rerun()
    st.markdown("#### Append-only session activity")
    if register.events:
        st.dataframe([
            {"Sequence": event.sequence, "Timestamp (UTC)": event.occurred_at,
             "Actor": event.actor, "Action": event.action,
             "Request": event.request_id, "Details": event.detail}
            for event in register.events
        ], width="stretch", hide_index=True)
    else:
        st.caption("No approval activity recorded in this session yet.")
    if st.button("Reset fictional approval session", key="reset_approval_register"):
        st.session_state.approval_register = ApprovalRegister()
        st.rerun()
