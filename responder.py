from retriever import retrieve_similar

def generate_response(issue, status, company=None):
    issue_lower = issue.lower()
    company = (company or "").lower()

    # 🚨 Escalation case
    if status == "escalated":
        if "visa" in company:
            return "This appears to be a sensitive payment or card-related issue. We are escalating it to Visa support for secure handling."
        elif "hackerrank" in company:
            return "This issue requires manual review from the HackerRank team. We are escalating it."
        elif "claude" in company:
            return "This request involves account or system-level concerns. Escalating to Claude support."
        return "This issue requires human assistance. We are escalating your request."

    # 🔍 Try similarity-based response
    match = retrieve_similar(issue)
    if match is not None:
        return match["response"]

    # 🎯 Company-specific fallback responses

    if "hackerrank" in company:
        if "test" in issue_lower or "assessment" in issue_lower:
            return "Please check your assessment settings or reconnect with the test link. If the issue persists, contact the test administrator."
        if "login" in issue_lower:
            return "Try resetting your password or logging in using the correct credentials."

    elif "visa" in company:
        if "payment" in issue_lower or "card" in issue_lower:
            return "Please verify your card details and ensure sufficient balance. If the issue continues, contact your bank or Visa support."
        if "fraud" in issue_lower:
            return "Immediately report unauthorized transactions to your bank or Visa support for secure handling."

    elif "claude" in company:
        if "api" in issue_lower or "integration" in issue_lower:
            return "Please verify your API key and integration setup. Refer to Claude documentation for correct configuration."
        if "account" in issue_lower:
            return "Check your account settings or permissions. If access issues persist, contact support."

    # 🧾 Generic fallback
    return "Thanks for reaching out. Please refer to the support documentation or contact support if the issue persists."