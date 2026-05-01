def detect_product_area(issue, company=""):
    issue = issue.lower()

    if "payment" in issue or "card" in issue:
        return "billing"
    if "test" in issue or "assessment" in issue:
        return "assessment"
    if "login" in issue or "account" in issue:
        return "account"

    return "general"