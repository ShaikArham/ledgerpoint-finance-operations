# Phase 6.1: Local interactive dashboard

## Start locally
From the repository root on Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit, typically http://localhost:8501.

## Pages
- Overview: revenue, expenses, net profit and reconciliation exceptions
- Invoices: fictional customer/supplier invoices and outstanding balances
- Bank reconciliation: matched and unmatched items, CSV export
- Financial reports: simplified P&L, balance sheet, trial balance and CSV export
- Controls: month-end checks and explicit limitations

## Limitations
This is a read-only guided scenario. It does not yet provide invoice editing,
file upload, arbitrary transaction entry, multi-user accounts or durable storage.
Amounts and VAT rates are illustrative. No live deployment or mobile test is
claimed. The Python accounting engine remains the calculation source of truth.

## Next
Run local tests and manually verify all five tabs, CSV downloads, mobile
layout and exception counts. Then add controlled user interactions and
deployment configuration.
