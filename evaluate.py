"""Run the agent on data/test_tickets.csv and report accuracy.

Usage (from the project folder, next to main.py):
    python main.py --input data/test_tickets.csv --output output/test_output.csv
    python evaluate.py
"""
import csv

exp = {r["issue"]: r for r in csv.DictReader(open("data/test_tickets.csv", encoding="utf-8"))}
out = list(csv.DictReader(open("output/test_output.csv", encoding="utf-8")))

n = len(out)
type_ok = status_ok = tp = fp = fn = 0
for r in out:
    e = exp[r["issue"]]
    type_ok += r["request_type"] == e["expected_type"]
    status_ok += r["status"] == e["expected_status"]
    got, want = r["status"] == "escalated", e["expected_status"] == "escalated"
    tp += got and want
    fp += got and not want
    fn += (not got) and want
    if r["request_type"] != e["expected_type"] or r["status"] != e["expected_status"]:
        print(f"MISS [{r['company']}] {r['issue'][:60]} | got {r['request_type']}/{r['status']}"
              f" | expected {e['expected_type']}/{e['expected_status']}")

print(f"\nTickets: {n}")
print(f"Request-type accuracy:      {type_ok}/{n} = {type_ok/n:.0%}")
print(f"Reply-vs-escalate accuracy: {status_ok}/{n} = {status_ok/n:.0%}")
print(f"Escalation precision: {tp}/{tp+fp} = {tp/(tp+fp):.0%}   recall: {tp}/{tp+fn} = {tp/(tp+fn):.0%}")
