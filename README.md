# LedgerPoint

**A fictional finance-operations simulator built with Python and Streamlit.**

LedgerPoint is an independent portfolio work sample demonstrating how invoice processing, double-entry accounting, payment allocation, bank reconciliation and financial reporting can work together in one auditable-in-process workflow.

> **Important:** This is an educational demonstration, not accounting software for real businesses. All entities and transactions are fictional. VAT rates are illustrative and are **not** a statement of Irish tax rules. LedgerPoint is not affiliated with DataPoint Ireland.

## What you can explore

| Area | Implemented demonstration |
| --- | --- |
| Accounting controls | Balanced journals, account validation, period locks, journal reversals and trial balance |
| Invoice operations | Sales and purchase invoices, CSV intake and illustrative VAT amounts |
| Payments | Customer receipts, supplier payments, outstanding balances and ageing |
| Reconciliation | Reference and amount matching, duplicate detection and unmatched bank transactions |
| Reporting | Profit and loss, simplified balance sheet, monthly results, budget variance and close checks |
| Web dashboard | Five read-only Streamlit sections and CSV downloads |
| Quality | 90 automated tests verified locally as of Phase 4.3; dashboard testing ongoing |

The dashboard runs a deterministic fictional scenario. It does **not** yet allow editing transactions, importing user files through the browser or storing changes permanently.

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
