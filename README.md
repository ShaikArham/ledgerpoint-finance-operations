# LedgerPoint

## New standalone website (HTML / CSS / JavaScript)

The repository now contains a separate premium, read-only finance operations case-study frontend:

- `index.html` — accessible single-page structure, executive overview, reconciliation, invoices, financial performance and case study
- `styles.css` — responsive navy/teal design system, KPI cards, animated hero and mobile navigation
- `script.js` — hash-based navigation and view switching, without external libraries
- `assets/logo.svg` — original LedgerPoint vector logo
- `.github/workflows/deploy-website.yml` — GitHub Pages deployment workflow (requires GitHub Pages to be enabled with GitHub Actions as source)

**Separate demos:** The standalone website is a curated fictional case study. The original `app.py` Streamlit application and its interactive Python finance controls remain available at https://ledgerpoint-finance-operations.streamlit.app/.

**Verification:** The HTML/CSS/JS website is committed but browser rendering, mobile visual QA and public GitHub Pages deployment are not yet independently confirmed. The prior 209-test GitHub Actions result applies to an earlier Python PR commit and does not certify the new frontend.


**A fictional finance-operations simulator built with Python and Streamlit.**

LedgerPoint is an independent portfolio work sample demonstrating how invoice processing, double-entry accounting, payment allocation, bank reconciliation and financial reporting can work together in one auditable-in-process workflow.

> **Important:** This is an educational demonstration, not accounting software for real businesses. All entities and transactions are fictional. VAT rates are illustrative and are **not** a statement of Irish tax rules. LedgerPoint is not affiliated with DataPoint Ireland.

## Current workstream status (November 2026)

Workstreams 1–8 were implemented earlier. Workstreams 9–14 are committed in the repository, including CSV staging, exception case management, budget scenarios, cash movement and a fictional payroll demonstration, and session-only maker-checker approvals with activity history.

**Verification limitation:** GitHub source and commits have been inspected, but a passing current pytest run, GitHub Actions workflow and deployed Streamlit end-to-end tests have **not** been independently confirmed for Workstreams 9–14. Treat these features as implemented, not QA-signed-off. Older test counts elsewhere in this README refer only to earlier project phases.

**Approval/audit disclaimer:** The approvals tab uses fictional, self-entered actors and session-only append-style events. It has no authentication, permanent storage, cryptographic integrity guarantees or real financial authorisation. Approvals never post transactions.\n\n**Payroll disclaimer:** The payroll tab uses a user-entered *fictional deduction percentage*. It does not calculate Irish PAYE, USC, PRSI, pensions or tax credits, and is not suitable for payroll processing or statutory compliance.

**[Start with the 3-minute reviewer guide](REVIEWER_GUIDE.md)** · [Open the live demo](https://ledgerpoint-finance-operations.streamlit.app/) · [QA status](QA_STATUS.md)

## What you can explore

| Area | Implemented demonstration |
| --- | --- |
| Accounting controls | Balanced journals, account validation, period locks, journal reversals and trial balance |
| Invoice operations | Sales and purchase invoices, CSV intake and illustrative VAT amounts |
| Payments | Customer receipts, supplier payments, outstanding balances and ageing |
| Reconciliation | Reference and amount matching, duplicate detection and unmatched bank transactions |
| Reporting | Profit and loss, simplified balance sheet, monthly results, budget variance and close checks |
| Web dashboard | Twelve Streamlit tabs with isolated interactive demos and CSV downloads |
| Quality | Earlier phase test count is historical; current full-suite and deployment verification pending |

The dashboard runs a deterministic fictional baseline. Isolated journal, CSV staging, case management and approval interactions are available, but they do not persist across sessions or alter the baseline financial records.

## Run locally (Windows PowerShell)

Requires **Python 3.11 or newer** and Git.

```powershell
git clone https://github.com/ShaikArham/ledgerpoint-finance-operations.git
cd ledgerpoint-finance-operations
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If Python 3.11 is not installed, replace `py -3.11` with a suitable Python 3.11+ launcher. Streamlit normally prints a local URL such as `http://localhost:8501`.

Already cloned the project? Run:

```powershell
git pull origin main
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Example scenario

The built-in fictional October 2026 dataset includes:

- Sales invoice: EUR 1,000 net plus EUR 230 illustrative VAT
- Purchase invoice: EUR 300 net plus EUR 69 illustrative VAT
- Customer receipt: EUR 500, leaving EUR 730 receivable
- Supplier payment: EUR 369, fully settling the purchase
- Reported net profit: EUR 700
- Bank reconciliation: two matches and one unmatched bank transaction requiring investigation

The unmatched transaction is intentionally **not** automatically posted.

## Repository structure

```text
app.py                      Streamlit dashboard
src/ledgerpoint/            Finance operations and reporting engine
tests/                      Automated unit and integration-style tests
docs/                       Accounting assumptions, phase notes and limitations
requirements-dashboard.txt  Dashboard dependencies
pyproject.toml              Python package and test dependencies
.github/workflows/          GitHub Actions test checks
```

## Project boundaries

- No real financial, employee, payroll or bank data
- No Irish statutory VAT or payroll calculations or filings
- No persistent database, multi-user permissions or immutable audit trail
- No bank API connection or automated bank exception resolution
- Simplified statements are **not** statutory financial statements
- Period-close checklist does not replace an accountant's review

## Development roadmap

- [x] Accounting foundation and validation
- [x] Invoice processing, settlement and reconciliation
- [x] Financial reporting and fictional end-to-end scenario
- [x] First read-only local dashboard
- [ ] Dashboard usability, accessibility and mobile verification
- [ ] Official-source Irish VAT/payroll research and carefully scoped illustrative workflows
- [ ] Public deployment and reproducible demonstration
- [ ] Final research paper, measured evaluation and application presentation

## Documentation

Start with [accounting rules](docs/ACCOUNTING-RULES.md), [job-role mapping](docs/JD-MAPPING.md), [dashboard setup](docs/PHASE-6-1.md) and [paper outline](docs/PAPER-OUTLINE.md).

**Author:** Shaik Arham Saquib. Independent portfolio project.
