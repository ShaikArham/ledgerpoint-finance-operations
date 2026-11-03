# Phase 3.1: Invoice intake

## Purpose
Demonstrate a core Accounts & Payroll Analyst responsibility: validating
sales and purchase invoices before posting to the ledger.

## Features
- Fictional sales and purchase invoice models
- Invoice reference, counterparty, date, currency and amount validation
- Duplicate reference detection scoped by invoice type and counterparty
- Illustrative VAT arithmetic with explicit Decimal rounding
- Gross invoice totals and sales/purchase register
- Ten automated test cases

## Important limits
- VAT rates in test data are illustrative; this module does not determine
  Irish VAT treatment, recoverability, exemptions, tax point or filing.
- This is an in-memory register, not an accounting ledger.
- No actual CSV/XLSX import, database, approvals or posting yet.
- No external systems, customer data or Revenue submissions.
- Amounts are in EUR and no foreign-currency processing is implemented.

## Next
Add explicit counterparty records and CSV import validation, then controlled
invoice posting to accounts receivable/payable and the general ledger.
