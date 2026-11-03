# Phase 4.3: End-to-end fictional demonstration

The demo in `ledgerpoint.demo.build_demo()` constructs fictional customers,
suppliers, a sales invoice, a purchase invoice, a partial customer receipt
and a fully settled supplier payment.

## Expected outputs
- Sales invoice: net EUR 1,000 + illustrative VAT EUR 230 = EUR 1,230
- Purchase invoice: net EUR 300 + illustrative VAT EUR 69 = EUR 369
- Customer receipt: EUR 500; outstanding receivable EUR 730
- Supplier payment: EUR 369; outstanding payable EUR 0
- Bank ledger net movement: EUR 131
- Revenue EUR 1,000; expenses EUR 300; net profit EUR 700
- Bank reconciliation: two matched references, one bank-only exception
- Balanced simplified balance sheet
- CSV exports for trial balance and reconciliation exceptions

## Usage
Run `python -m pytest -q` to execute all tests. The demo is currently a
Python API, not a browser-based interactive application. No file-writing
or network access occurs in the demo.

## Limits
All entities and transactions are fictional. VAT rates are illustrative,
not a representation of correct Irish VAT classification. Bank-only
transactions are flagged but not automatically posted. No persistent
storage, authorisation, document attachments, statutory financial
statements, or payroll processing exists yet. The demo intentionally
shows a reconciliation exception to support a future review workflow.
