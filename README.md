# LedgerPoint

Independent applicant work sample: Accounts, Payroll & Finance Operations Simulator.

**Status:** Phase 1 foundation. Not a finished accounting or payroll product.

**Disclaimer:** Not affiliated with DataPoint Ireland. All example records are fictional. No real tax or payroll submissions.

## Roadmap
1. Foundation, JD mapping and documented accounting rules
2. Double-entry ledger and trial balance
3. Invoices, payments, bank reconciliation, receivables/payables
4. P&L, balance sheet and variance reporting
5. Irish VAT and payroll review workflows (illustrative, verified against official sources)
6. Web UI, guided demo and exports
7. Automated tests, CI and deployment
8. Research-style paper with measured results and limitations

## Run tests
```bash
python -m venv .venv
# Activate the virtual environment
pip install -e '.[dev]'
pytest -q
```

## Architecture
Financial rules belong in a testable deterministic backend. Use Decimal, not floating point, for monetary amounts. No AI-based posting decisions. Future web UI is separate from accounting calculations.

## Documentation
See `docs/JD-MAPPING.md`, `docs/ACCOUNTING-RULES.md`, and `docs/PAPER-OUTLINE.md`.
