# Phase 2: Accounting engine

## Implemented in this milestone
- Fictional chart of accounts with five account categories
- In-memory double-entry journal posting
- Unique journal IDs and account-code validation
- Signed trial balances (debit positive, credit negative)
- Additional automated tests for posting and controls

## Example
An owner deposits EUR 250 into the business:
- Debit Bank (1000) EUR 250
- Credit Owner capital (3000) EUR 250

The trial balance nets to zero because debits equal credits.

## Explicit limitations
- No database persistence or user accounts
- No immutable audit log or correction/reversal workflow
- No period close, tax calculations or statutory filings
- Not suitable for real client financial records

## Next acceptance criteria
Introduce immutable posting history, reversals, reporting periods and ledger-to-statement tests before building invoice workflows.
