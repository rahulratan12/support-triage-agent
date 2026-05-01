"""Decides whether a ticket is `replied` or `escalated`.

Wraps the hard-rule engine in `safety.py` and falls back to a final
"replied" status when no rule fires. Returns a (status, reason, response)
triple so callers can use the canned safety reply when applicable.

Backwards-compatible: `decide_status(issue)` still returns the status
string for older callers.
"""
from __future__ import annotations

from safety import evaluate


def decide_status_full(
    issue: str,
    subject: str = "",
    company: str = "",
) -> tuple[str, str, str]:
    """Return (status, reason, canned_response).

    - status: "replied" or "escalated"
    - reason: short justification string explaining the decision
    - canned_response: only set when safety layer wants a specific reply
      (out-of-scope, pleasantry); empty otherwise so the responder fills it.
    """
    decision = evaluate(issue=issue, subject=subject, company=company)

    if decision.action == "escalate":
        return "escalated", decision.reason, ""

    if decision.action in ("replied_out_of_scope", "replied_pleasantry"):
        return "replied", decision.reason, decision.response

    return "replied", "", ""


def decide_status(issue, subject: str = "", company: str = ""):
    """Backwards-compatible: returns just the status string."""
    status, _, _ = decide_status_full(issue, subject=subject, company=company)
    return status
