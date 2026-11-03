# Phase 3.3: Counterparties, settlements and ageing

## Scope
- Fictional customer/supplier master records
- Invoice posting after party validation
- Partial and multiple invoice-specific payments
- Receipt/payment double-entry postings to bank and receivables/payables
- Outstanding balances as of a chosen date
- Ageing buckets: not due, 0–30, 31–60, 61–90 and 90+ days
- Default chart includes illustrative input VAT account

## Accounting controls
- Payment must reference an existing invoice
- No over-allocation or duplicate payment ID
- Closed-period posting is rejected by ControlledLedger
- All amounts use Decimal and posted journals must balance

## Limitations
- In-memory educational simulator only
- Payment ID is globally unique; one payment cannot yet be allocated across multiple invoices
- No bank statement reconciliation or unallocated receipts yet
- No persistent audit log, user permissions, or transactional database
- Ageing combines sales and purchase invoices; separate debtor and creditor views are a future task
- VAT figures are illustrative and not a tax determination
- Date validation does not enforce chronological payment entry across existing allocations
