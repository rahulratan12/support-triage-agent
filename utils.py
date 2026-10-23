def detect_product_area(issue, company):
    text = (issue or "").lower()

    if "payment" in text or "refund" in text:
        return "payments"
    if "login" in text or "account" in text:
        return "account_management"
    if "test" in text or "score" in text:
        return "assessments"

    return "general"


def generate_justification(issue, status, request_type):
    if status == "escalated":
        return "Detected high-risk or sensitive request → escalated to human."

    return f"Classified as {request_type} using keyword logic and handled automatically."

import csv
import os


class Logger:
    """Simple file logger that can also echo to the terminal."""

    def __init__(self, path, echo=False):
        self.echo = echo
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._f = open(path, "w", encoding="utf-8")

    def write(self, msg):
        self._f.write(str(msg) + "\n")
        self._f.flush()
        if self.echo:
            print(msg)

    def close(self):
        self._f.close()


def read_csv(path):
    """Read a CSV into a list of dicts with lower-cased column names."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [
            {(k or "").strip().lower(): (v or "") for k, v in row.items()}
            for row in csv.DictReader(f)
        ]


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
