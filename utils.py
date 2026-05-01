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