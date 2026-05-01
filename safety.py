"""Hard safety / escalation rules.

These rules trigger BEFORE any LLM-generated response. If a rule matches, the
ticket is forced to `escalated` (or in some cases `replied` with a fixed
out-of-scope message) regardless of what the responder says. This keeps the
agent from hallucinating policies on sensitive cases.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SafetyDecision:
    action: str            # "escalate", "replied_out_of_scope", "replied_pleasantry", or ""
    reason: str            # human-readable justification
    response: str = ""     # canned response when action == "replied_*"


# --- patterns ---------------------------------------------------------------

_PLEASANTRY_RE = re.compile(
    r"^\s*(thanks?|thank you|thx|cheers|appreciate it|great|awesome|nice|"
    r"hi|hello|hey|bye|goodbye)\b[!.\s]*$",
    re.IGNORECASE,
)

_OUT_OF_SCOPE_RE = re.compile(
    r"\b(actor|actress|movie|tv show|song lyrics|recipe|stock price|"
    r"who won|capital of|translate this|joke|poem|essay|homework|"
    r"weather in|news today)\b",
    re.IGNORECASE,
)

# Generic "delete files / give me code" requests we should never produce code for.
_HARMFUL_CODE_RE = re.compile(
    r"\b("
    r"give me .*code .* delete|"
    r"code to delete|"
    r"script to delete|"
    r"rm\s*-rf|"
    r"format\s+c:|"
    r"erase .*all files|"
    r"wipe .*disk"
    r")\b",
    re.IGNORECASE,
)

# Prompt-injection / "show me your internal rules" probes.
_PROMPT_INJECTION_RE = re.compile(
    r"\b(show|reveal|print|display|expose|dump|disclose|"
    r"affiche|montre|muestra|enseña|"
    r"ignore (previous|all) instructions|"
    r"system prompt|your prompt|your instructions|"
    r"internal rules|internal logic|exact (logic|criteria)|"
    r"r[èe]gles internes|reglas internas|prompt interno|"
    r"retrieved (docs|documents)|"
    r"documents r[ée]cup[ée]r[ée]s)\b",
    re.IGNORECASE,
)

# High-risk / sensitive Visa cases that should always go to a human.
_VISA_FRAUD_RE = re.compile(
    r"\b(identity (theft|stolen)|fraud|fraudulent|"
    r"unauthorized (charge|transaction)|"
    r"my card was used)\b",
    re.IGNORECASE,
)

# Refund / charge dispute language that requires a human/billing team.
_REFUND_DEMAND_RE = re.compile(
    r"\b(refund (me|my)|"
    r"give me (my )?(money|refund)|"
    r"chargeback|charge ?back|"
    r"reverse (the|this) (charge|payment)|"
    r"cs_live_[a-z0-9]+|"
    r"order id:?\s*[a-z0-9_]+)\b",
    re.IGNORECASE,
)

# Demands that go beyond what support can do.
_OVERREACH_RE = re.compile(
    r"\b("
    r"increase my score|"
    r"override .* (decision|rejection)|"
    r"move me to the next round|"
    r"tell the company to|"
    r"force .* to (refund|advance)|"
    r"ban (the|that) (seller|merchant)|"
    r"restore my access immediately"
    r")\b",
    re.IGNORECASE,
)

# Major outages / "site is down" -> escalate engineering.
_PLATFORM_DOWN_RE = re.compile(
    r"\b("
    r"site is down|website is down|all pages|"
    r"resume builder is down|"
    r"completely (down|stopped|broken)|"
    r"all requests (are )?failing|"
    r"none of the (submissions|pages) (are )?(working|accessible)"
    r")\b",
    re.IGNORECASE,
)

# Vague / no-info messages.
_TOO_VAGUE_RE = re.compile(
    r"^\s*(it'?s? not working|help( me)?|need help|please help|"
    r"having issues|having problems|.{0,20}help.{0,20})\s*$",
    re.IGNORECASE,
)

# Security vulnerability / bug bounty submissions.
_SECURITY_REPORT_RE = re.compile(
    r"\b(bug bounty|security vulnerability|"
    r"found a (critical |major )?(bug|vulnerability)|"
    r"responsible disclosure|"
    r"penetration test|pen test|"
    r"vulnerability in claude)\b",
    re.IGNORECASE,
)

# Vendor security review / DPA / infosec questionnaire requests.
_INFOSEC_FORM_RE = re.compile(
    r"\b(infosec (process|review|form|questionnaire)|"
    r"vendor (security|risk) (review|assessment)|"
    r"fill (in |out )?(the )?forms?|"
    r"sign .*(dpa|msa|nda)|"
    r"security (questionnaire|review))\b",
    re.IGNORECASE,
)


def evaluate(issue: str, subject: str = "", company: str = "") -> SafetyDecision:
    """Run hard rules in priority order and return the first match."""
    text = f"{subject}\n{issue}".strip()

    # 1. Pleasantries — short reply, no escalation.
    if _PLEASANTRY_RE.match(issue.strip()):
        return SafetyDecision(
            action="replied_pleasantry",
            reason="Pleasantry / acknowledgement; no support action needed.",
            response="Happy to help",
        )

    # 2. Prompt-injection probes — never disclose internals.
    if _PROMPT_INJECTION_RE.search(text):
        return SafetyDecision(
            action="escalate",
            reason=(
                "Request appears to attempt prompt-injection or asks the agent to "
                "disclose its internal rules / retrieved documents; routed to a "
                "human reviewer."
            ),
        )

    # 3. Harmful code requests.
    if _HARMFUL_CODE_RE.search(text):
        return SafetyDecision(
            action="replied_out_of_scope",
            reason=(
                "Request asks for destructive code outside the support corpus; "
                "the agent does not generate such instructions."
            ),
            response=(
                "I am sorry, this is out of scope from my capabilities. "
                "I can only help with HackerRank, Claude, or Visa support topics."
            ),
        )

    # 4. Trivia / generic-knowledge questions.
    if _OUT_OF_SCOPE_RE.search(text):
        return SafetyDecision(
            action="replied_out_of_scope",
            reason="Question is outside the HackerRank/Claude/Visa support scope.",
            response="I am sorry, this is out of scope from my capabilities",
        )

    # 5. Identity theft / fraud (Visa) — always escalate to issuer/human.
    if _VISA_FRAUD_RE.search(text):
        return SafetyDecision(
            action="escalate",
            reason=(
                "Identity theft or fraud claim: Visa requires the cardholder to "
                "act through their issuing bank; routed to a human agent for "
                "safe handling."
            ),
        )

    # 6. Refund / chargeback demands — billing team.
    if _REFUND_DEMAND_RE.search(text):
        return SafetyDecision(
            action="escalate",
            reason=(
                "Refund or charge-dispute request requires access to billing "
                "records and merchant/issuer coordination that this agent does "
                "not have."
            ),
        )

    # 7. Overreach (override hiring decision, ban a merchant, restore seat...).
    if _OVERREACH_RE.search(text):
        return SafetyDecision(
            action="escalate",
            reason=(
                "Request asks the agent to take an action outside its authority "
                "(override a hiring decision, force a refund, ban a merchant, "
                "or restore an admin-removed seat). Routed to a human."
            ),
        )

    # 8. Platform-wide outage.
    if _PLATFORM_DOWN_RE.search(text):
        return SafetyDecision(
            action="escalate",
            reason="Reported platform-wide outage; needs engineering visibility.",
        )

    # 9. Security vulnerability disclosure.
    if _SECURITY_REPORT_RE.search(text):
        return SafetyDecision(
            action="escalate",
            reason=(
                "Security vulnerability or bug bounty submission; route to the "
                "appropriate disclosure channel (HackerOne / Responsible "
                "Disclosure) rather than answer inline."
            ),
        )

    # 10. Infosec / vendor-review forms.
    if _INFOSEC_FORM_RE.search(text):
        return SafetyDecision(
            action="escalate",
            reason=(
                "Vendor security review / infosec questionnaire belongs to the "
                "Sales / Trust team, not self-service support."
            ),
        )

    # 11. Vague messages.
    if _TOO_VAGUE_RE.match(issue.strip()) or len(issue.strip()) < 12:
        return SafetyDecision(
            action="escalate",
            reason=(
                "Message is too vague to identify the product or problem; "
                "needs a human to ask clarifying questions."
            ),
        )

    return SafetyDecision(action="", reason="")
