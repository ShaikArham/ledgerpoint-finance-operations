"""Illustrative payroll operations, NOT an Irish statutory payroll calculator.

All deduction percentages are user-provided training assumptions, never PAYE,
USC, PRSI, Revenue rates, tax credits, or employer filing calculations.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")

@dataclass(frozen=True)
class PayrollInput:
    employee_id: str
    hours: Decimal
    hourly_rate: Decimal
    deduction_pct: Decimal

@dataclass(frozen=True)
class Payslip:
    employee_id: str
    gross: Decimal
    illustrative_deduction: Decimal
    net: Decimal

def money(value: str, field: str, *, maximum: Decimal | None = None) -> Decimal:
    try:
        result = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"{field}: enter a valid number") from None
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field}: must be finite and non-negative")
    if maximum is not None and result > maximum:
        raise ValueError(f"{field}: exceeds allowed demonstration limit")
    return result

def calculate_payroll(entry: PayrollInput) -> Payslip:
    if not entry.employee_id.strip():
        raise ValueError("Employee reference is required")
    for label, amount in (("Hours", entry.hours), ("Hourly rate", entry.hourly_rate),
                          ("Deduction percentage", entry.deduction_pct)):
        if not amount.is_finite() or amount < 0:
            raise ValueError(f"{label} must be finite and non-negative")
    if entry.hours > 744 or entry.hourly_rate > 10000:
        raise ValueError("Hours or hourly rate exceeds demonstration limit")
    if entry.deduction_pct > 100:
        raise ValueError("Deduction percentage cannot exceed 100")
    if entry.hours.as_tuple().exponent < -2 or entry.hourly_rate.as_tuple().exponent < -2 or entry.deduction_pct.as_tuple().exponent < -2:
        raise ValueError("Inputs support at most two decimal places")
    gross = (entry.hours * entry.hourly_rate).quantize(CENT, rounding=ROUND_HALF_UP)
    deduction = (gross * entry.deduction_pct / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP)
    return Payslip(entry.employee_id.strip(), gross, deduction, gross - deduction)

def payroll_batch(entries: tuple[PayrollInput, ...]) -> tuple[Payslip, ...]:
    seen = set()
    results = []
    for entry in entries:
        key = entry.employee_id.strip().casefold()
        if key in seen:
            raise ValueError("Duplicate employee reference in payroll batch")
        seen.add(key)
        results.append(calculate_payroll(entry))
    return tuple(results)
