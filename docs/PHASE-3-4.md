# Phase 3.4: Reference-based bank reconciliation

## Workflow
Compare recorded fictional invoice settlements with fictional bank statement
transactions using exact payment IDs and bank references. A bank credit is
positive; a bank debit is negative.

## Outcomes
- matched
- ledger_only: payment in the ledger, absent from bank statement
- bank_only: bank transaction not represented by a recorded allocation
- amount_mismatch: matching reference but different signed amount
- duplicate_bank_reference: more than one statement row uses the same reference

The cutoff date excludes later-dated records. Summary counts support a future
reconciliation dashboard. Ten tests cover the main cases.

## Important limitations
- No bank feeds or actual bank account data
- Exact reference matching only; no fuzzy matching or confidence scoring
- No handling of bank charges, opening balances or uncleared deposits
- A single payment reference can represent only one invoice allocation
- Duplicate references are flagged but not individually itemised
- No persistence, approval workflow or multi-user access
- Not a production-ready bank reconciliation or financial control
