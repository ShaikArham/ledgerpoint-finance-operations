"""Session-scoped, fictional reconciliation case management.

Case notes and decisions do not modify or reconcile the underlying ledger.
"""
from dataclasses import dataclass, replace
from datetime import date
from typing import Optional

STATUSES = ("Open", "Investigating", "Awaiting evidence", "Resolved")
PRIORITIES = ("Low", "Medium", "High")

@dataclass(frozen=True)
class CaseEvent:
    when: str
    action: str
    note: str

@dataclass(frozen=True)
class ExceptionCase:
    case_id: str
    reference: str
    exception_type: str
    priority: str = "Medium"
    status: str = "Open"
    owner: str = "Unassigned"
    resolution: str = ""
    history: tuple[CaseEvent, ...] = ()

def create_case(case_id: str, reference: str, exception_type: str) -> ExceptionCase:
    if not case_id.strip() or not reference.strip() or not exception_type.strip():
        raise ValueError("Case ID, reference and exception type are required")
    return ExceptionCase(case_id.strip(), reference.strip(), exception_type.strip())

def update_case(case: ExceptionCase, *, status: str, priority: str, owner: str,
                note: str, resolution: str = "", event_date: Optional[date] = None) -> ExceptionCase:
    if status not in STATUSES or priority not in PRIORITIES:
        raise ValueError("Unknown case status or priority")
    if not owner.strip():
        raise ValueError("An owner is required")
    if status == "Resolved" and not resolution.strip():
        raise ValueError("A resolution explanation is required before closing a case")
    if case.status == "Resolved" and status != "Resolved":
        raise ValueError("Resolved cases cannot be reopened without a separate review")
    if not note.strip():
        raise ValueError("A case update note is required")
    event = CaseEvent(str(event_date or date.today()), f"{case.status} → {status}", note.strip())
    return replace(case, status=status, priority=priority, owner=owner.strip(),
                   resolution=resolution.strip() if status == "Resolved" else "",
                   history=case.history + (event,))
