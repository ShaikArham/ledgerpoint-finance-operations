# Phase 2.2: Posting history, reversals and period locks

## Implemented
- Dated journal records with unique IDs and descriptions
- Frozen posted journal records in an in-memory append-only list
- Reversals that preserve the original and swap debit/credit lines
- One reversal per original journal
- Closed month rejects postings and reversals dated inside that month
- Trial balance calculated as of a selected date
- Ten additional unit tests

## Accounting example
2026-10-31: Debit Bank EUR 250, Credit Owner Capital EUR 250.
2026-11-01: Reverse the journal, Debit Owner Capital EUR 250, Credit Bank EUR 250.
October as-of balance remains EUR 250; November as-of net balance is zero.

## Limitations and next steps
This is in-memory educational code, not a durable or tamper-resistant audit trail.
The posting API accepts an explicit reversal_of field, so real user permissions
and validation boundaries are not yet designed. Period locks are local to this
instance. No database, authentication, approval workflow, or statutory tax
calculations are implemented. Before real-world use, implement persistent
transactional storage, access control, signed audit history, multi-user concurrency
controls and a full accounting review.
