# LedgerPoint | Reviewer guide

**Independent fictional finance-operations portfolio demo. Not affiliated with DataPoint Ireland.**

[Open the interactive dashboard](https://ledgerpoint-finance-operations.streamlit.app/) · [Source code](https://github.com/ShaikArham/ledgerpoint-finance-operations) · [QA evidence and limitations](QA_STATUS.md)

## Start with the operational problem

A small fictional business has a customer invoice for €1,230, a supplier bill for €369, and three bank statement lines. Two bank entries match recorded settlements; a €12 outgoing transaction is unmatched. The system must **flag the difference rather than silently posting it**.

## Three-minute demonstration

1. **Overview (30 sec)** — Read the €1,000 revenue, €300 expense, €700 profit and one bank exception.
2. **Bank reconciliation (45 sec)** — Inspect `UNKNOWN-001`: the €12 bank-only item is not treated as a ledger expense.
3. **Invoices (30 sec)** — Inspect `SALE-001`: €1,230 gross less €500 allocated leaves €730 outstanding.
4. **Exception cases (30 sec)** — Create an investigation update and see session-scoped case history. The underlying reconciliation does not change.
5. **Approvals & audit (30 sec)** — Request an approval as a fictional maker, review it as a separate checker, and inspect the event sequence. No posting occurs.
6. **Financial reports (15 sec)** — Inspect the balanced trial balance and download a CSV.

## What the project demonstrates

- Deterministic double-entry and invoice settlement logic.
- Reconciliation with explicit unmatched-item handling.
- Operational exception triage and maker/checker workflow modelling.
- Data validation, staged CSV imports, and financial reporting.
- Automated test cases and documented limitations.

## What it does not demonstrate

This is not a production accounting product, real DataPoint Ireland data, professional accounting employment, statutory Irish payroll/VAT compliance, authenticated approvals or permanent audit storage. The payroll deduction percentage is a fictional user-defined assumption. Session-scoped actions reset and do not mutate the baseline ledger.

## More to explore

- **CSV staging:** upload and validate supported files without posting transactions.
- **Journal sandbox:** post balanced fictional entries to an isolated demonstration ledger.
- **Budget & forecast:** compare budget with actual and change what-if assumptions.
- **Cash flow:** inspect posted customer/supplier settlements and trade working capital.
- **Payroll demo:** explore a deliberately non-statutory gross-to-net illustration.

## Verification status

The source and tests for Workstreams 9–14 have been committed. The current full pytest suite, GitHub Actions result, live deployment and mobile responsiveness have **not** been independently verified as passing. See [QA_STATUS.md](QA_STATUS.md) for the evidence register.

**Portfolio focus:** practical data quality, finance-operations controls, traceable exceptions and readable reporting, not claims of professional payroll or accounting practice.
