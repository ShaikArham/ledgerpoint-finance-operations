# Accounting rules and controls (initial draft)

- Monetary values use Python `Decimal` and EUR precision of at most two decimal places.
- Each posted journal must balance: total debits equal total credits.
- Journal lines must have a valid account and either debit or credit, never both.
- Posting, correction, reversal and audit history will be designed before production-like workflows.
- Payment allocation must not silently resolve ambiguous invoice references.
- VAT and payroll calculations remain **out of scope** until official Irish rules and dates are sourced and tests defined.
- This simulator is educational and must not be used for real filings or payroll.
