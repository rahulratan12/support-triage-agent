"""Terminal entry-point for the multi-domain support triage agent.

For each ticket:
  1. classify the request type        (classifier.classify_request)
  2. decide reply vs. escalate        (escalation.decide_status)
  3. detect a product area            (utils.detect_product_area)
  4. compose a grounded response      (responder.generate_response)
  5. write a justification line       (utils.generate_justification)

Outputs a CSV with: issue, subject, company, status, product_area,
response, justification, request_type.

Usage (terminal):
    python main.py
    python main.py --input data/input.csv --output output/output.csv
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import traceback

# Make sibling modules importable regardless of cwd.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from classifier import classify_request
from escalation import decide_status, decide_status_full
from responder import generate_response
from utils import (
    Logger,
    detect_product_area,
    generate_justification,
    read_csv,
    write_csv,
)

DEFAULT_INPUT_CANDIDATES = (
    os.path.join(_THIS_DIR, "data", "input.csv"),
    os.path.join(_THIS_DIR, "data", "support_tickets.csv"),
    os.path.join(os.getcwd(), "support_tickets.csv"),
)
DEFAULT_OUTPUT = os.path.join(_THIS_DIR, "output", "output.csv")
DEFAULT_LOG = os.path.join(_THIS_DIR, "data", "log.txt")

OUTPUT_FIELDS = [
    "issue", "subject", "company",
    "status", "product_area", "response", "justification", "request_type",
]


def _resolve_input(path: str | None) -> str:
    if path:
        if not os.path.exists(path):
            sys.exit(f"Input file not found: {path}")
        return path
    for p in DEFAULT_INPUT_CANDIDATES:
        if os.path.exists(p):
            return p
    sys.exit(
        "No input CSV found. Looked in:\n  "
        + "\n  ".join(DEFAULT_INPUT_CANDIDATES)
        + "\nPass --input <path> explicitly."
    )


def _row_value(row: dict, *keys: str) -> str:
    for k in keys:
        v = row.get(k.lower())
        if v:
            return v
    return ""


def process_row(row: dict, logger: Logger) -> dict:
    issue = _row_value(row, "issue")
    subject = _row_value(row, "subject")
    company = _row_value(row, "company")

    # Safety / escalation gate: status + reason + (optional) canned reply.
    status, safety_reason, canned = decide_status_full(
        issue=issue, subject=subject, company=company,
    )

    request_type = classify_request(issue)
    if not issue or not issue.strip():
        request_type = "invalid"

    product_area = detect_product_area(issue, company)

    if status == "escalated":
        response = "Escalate to a human"
    elif canned:
        response = canned
    else:
        try:
            response = generate_response(issue, status, company)
        except Exception:
            logger.write("responder error:\n" + traceback.format_exc())
            response = (
                "I couldn't compose a grounded answer; please contact support directly."
            )
            status = "escalated"
            safety_reason = (
                safety_reason
                or "Responder failed to ground answer in corpus; routed to a human."
            )

    justification = generate_justification(issue, status, request_type)
    if safety_reason:
        # Layer the specific safety reason on top of the generic justification
        # so the user can see WHY the safety rule fired.
        justification = f"{safety_reason} ({justification})"

    return {
        "issue": issue,
        "subject": subject,
        "company": company,
        "status": status,
        "product_area": product_area,
        "response": response,
        "justification": justification,
        "request_type": request_type,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Multi-domain support triage agent")
    p.add_argument("--input", help="Path to input CSV (defaults to data/input.csv).")
    p.add_argument("--output", default=DEFAULT_OUTPUT, help="Path to output CSV.")
    p.add_argument("--log", default=DEFAULT_LOG, help="Path to run log.")
    p.add_argument("--echo", action="store_true", help="Print each row as processed.")
    args = p.parse_args(argv)

    input_path = _resolve_input(args.input)

    logger = Logger(path=args.log, echo=args.echo)
    logger.write(f"input: {input_path}")
    logger.write(f"output: {args.output}")

    try:
        rows = read_csv(input_path)
    except Exception:
        logger.write("failed to read input CSV:\n" + traceback.format_exc())
        return 2

    if not rows:
        logger.write("no rows; nothing to do.")
        return 0

    results = []
    t0 = time.time()
    for i, row in enumerate(rows, start=1):
        result = process_row(row, logger)
        results.append(result)
        logger.write(
            f"[{i}/{len(rows)}] status={result['status']} "
            f"product_area={result['product_area']} "
            f"request_type={result['request_type']}"
        )

    write_csv(args.output, results, fieldnames=OUTPUT_FIELDS)
    logger.write(f"wrote {len(results)} rows to {args.output} in {time.time()-t0:.1f}s")
    logger.close()

    print(f"Done. {len(results)} rows -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
