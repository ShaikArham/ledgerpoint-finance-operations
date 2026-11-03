# Phase 5.1 — Guided reconciliation investigation

The bank reconciliation page now supports selecting a fictional transaction to view a plain-language explanation, amount comparison and next action.

This is **read-only triage**, not an accounting adjustment. Selecting a transaction does not create journal entries, clear an exception, or change financial statements. An unmatched bank line remains unresolved until supported evidence is reviewed and the underlying data is corrected using accounting controls.

The existing reconciliation engine and its test cases are unchanged. The new `ledgerpoint.triage` module covers five known statuses and rejects unknown statuses.

Suggested walkthrough for a reviewer:
1. Open Bank reconciliation.
2. Select `UNKNOWN-001`.
3. See the bank-only exception and its €12.00 outgoing amount.
4. Review suggested investigation steps.
5. Export the reconciliation CSV for follow-up.

All parties, transactions and VAT rates are fictional or illustrative. This is not a statutory reconciliation or an automated banking integration.
