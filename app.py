import streamlit as st
from classifier import classify_request
from escalation import decide_status
from utils import detect_product_area, generate_justification
from responder import generate_response

st.title("🤖 Support Triage Agent")

issue = st.text_area("Enter your issue:")
company = st.selectbox("Select company", ["HackerRank", "Claude", "Visa"])

if st.button("Submit"):
    request_type = classify_request(issue)
    status = decide_status(issue)
    product_area = detect_product_area(issue, company)
    response = generate_response(issue, status, company)
    justification = generate_justification(issue, status, request_type)

    st.subheader("Result")
    st.write("Status:", status)
    st.write("Product Area:", product_area)
    st.write("Request Type:", request_type)
    st.write("Response:", response)
    st.write("Justification:", justification)