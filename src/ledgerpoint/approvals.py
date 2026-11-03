"""Session-only maker/checker approvals and append-only operational events.

Educational controls, not authenticated identities or tamper-proof audit storage.
No action posts to the ledger or changes reconciliation results.
"""
from dataclasses import dataclass, replace
from datetime import datetime, timezone

@dataclass(frozen=True)
class Activity:
    sequence: int
    occurred_at: str
    actor: str
    action: str
    request_id: str
    detail: str

@dataclass(frozen=True)
class Approval:
    request_id: str
    reference: str
    requested_by: str
    reason: str
    status: str = "Pending"
    reviewed_by: str = ""
    review_note: str = ""

@dataclass(frozen=True)
class ApprovalRegister:
    requests: tuple[Approval, ...] = ()
    events: tuple[Activity, ...] = ()

def _required(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    if len(value.strip()) > 500:
        raise ValueError(f"{label} is too long")
    return value.strip()

def _event(register: ApprovalRegister, actor: str, action: str, request_id: str,
           detail: str, at: datetime | None) -> Activity:
    moment = at or datetime.now(timezone.utc)
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("Audit timestamp must include a timezone")
    return Activity(len(register.events) + 1, moment.isoformat(), actor, action, request_id, detail)

def request_approval(register: ApprovalRegister, *, request_id: str, reference: str,
                     actor: str, reason: str, at: datetime | None = None) -> ApprovalRegister:
    request_id = _required(request_id, "Request ID")
    reference = _required(reference, "Reference")
    actor = _required(actor, "Requester")
    reason = _required(reason, "Reason")
    if any(x.request_id.casefold() == request_id.casefold() for x in register.requests):
        raise ValueError("Duplicate approval request ID")
    approval = Approval(request_id, reference, actor, reason)
    event = _event(register, actor, "Requested", request_id, reason, at)
    return replace(register, requests=register.requests + (approval,),
                   events=register.events + (event,))

def review_approval(register: ApprovalRegister, *, request_id: str, actor: str,
                    decision: str, note: str, at: datetime | None = None) -> ApprovalRegister:
    actor = _required(actor, "Reviewer")
    note = _required(note, "Review note")
    if decision not in ("Approved", "Rejected"):
        raise ValueError("Decision must be Approved or Rejected")
    request_id = _required(request_id, "Request ID")
    index = next((i for i, x in enumerate(register.requests)
                  if x.request_id.casefold() == request_id.casefold()), None)
    if index is None:
        raise ValueError("Approval request not found")
    current = register.requests[index]
    if current.status != "Pending":
        raise ValueError("Approval has already been reviewed")
    if current.requested_by.casefold() == actor.casefold():
        raise ValueError("Requester cannot approve or reject their own request")
    updated = replace(current, status=decision, reviewed_by=actor, review_note=note)
    event = _event(register, actor, decision, current.request_id, note, at)
    requests = list(register.requests)
    requests[index] = updated
    return replace(register, requests=tuple(requests), events=register.events + (event,))
