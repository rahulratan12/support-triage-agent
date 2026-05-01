"""Pretty-prints the output CSV for quick eyeballing."""
import csv
import sys
import textwrap

with open("output/output.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

for i, r in enumerate(rows, 1):
    issue = (r["issue"] or "").replace("\n", " ").strip()
    if len(issue) > 90:
        issue = issue[:87] + "..."
    response = (r["response"] or "").replace("\n", " ").strip()
    if len(response) > 200:
        response = response[:197] + "..."
    just = (r["justification"] or "").replace("\n", " ").strip()
    if len(just) > 130:
        just = just[:127] + "..."
    print(
        f"[{i:>2}] company={r['company']:<11} status={r['status']:<9} "
        f"area={r['product_area']:<22} type={r['request_type']}"
    )
    print(f"     issue: {issue}")
    print(f"     resp:  {response}")
    print(f"     just:  {just}")
    print()
