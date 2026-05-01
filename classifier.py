def classify_request(issue):
    issue = issue.lower()

    if any(word in issue for word in ["error", "not working", "failed", "bug", "down"]):
        return "bug"

    if any(word in issue for word in ["feature", "add", "improve", "request"]):
        return "feature_request"

    if any(word in issue for word in ["payment", "account", "login", "access", "card", "refund"]):
        return "product_issue"

    return "invalid"