# Phase 3.2: CSV invoice intake and journal integration

## Features
- Strict eight-column CSV parsing, per-row error reporting
- Reuse existing invoice validation and duplicate checks
- Sales invoice: debit receivables, credit revenue and illustrative VAT control
- Purchase invoice: debit expense and illustrative input VAT, credit payables
- ControlledLedger posting with unique invoice-derived journal IDs
- Duplicate posting and closed-period rejection
- Ten additional unit tests

## Limitations
- Only fictional EUR transactions.
- VAT treatment is illustrative and not a compliance engine.
- Posting is not atomic across a persistent invoice register and ledger.
- No external CSV file upload UI yet, only a Python function accepting CSV text.
- Input VAT account is currently added manually in the purchase test; the
  chart of accounts should include this code as part of the next refinement.
- No supplier/customer master validation or payment allocations yet.

## Next
Unify the chart of accounts and add customer/supplier master records,
invoice status tracking, payment allocation and aged balance reports.
