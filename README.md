# 🧠 Support Triage Agent (HackerRank Orchestration Hackathon)

A multi-domain AI-powered support triage system that classifies, routes, and responds to support tickets across platforms like **HackerRank, Claude, and Visa**.

This project focuses on building a **safe, reliable, and non-hallucinating support assistant** using only a provided support corpus.

## 🚀 Features

- 🔍 **Request Classification**
  - Categorizes tickets into:
    - product_issue
    - feature_request
    - bug
    - invalid

- 🏢 **Product Area Detection**
  - Identifies relevant product domains dynamically

- ⚠️ **Safety-Aware Escalation**
  - Detects high-risk or sensitive requests
  - Escalates to human support when needed

- 📚 **Retrieval-Based Responses**
  - Uses corpus-based retrieval (no hallucination)
  - Returns grounded answers only

- 🧩 **Company-Aware Logic**
  - Adapts behavior based on platform (HackerRank / Claude / Visa)

- 🖥️ **Terminal-Based Pipeline**
  - Processes tickets in batch mode

- 🌐 **Streamlit UI (Optional)**
  - Interactive interface for testing

- 📝 **Logging System**
  - Tracks processing decisions for transparency


 📂 Project Structure
support-triage-agent/
│
├── main.py # Entry point (terminal pipeline)
├── app.py # Streamlit UI
├── classifier.py # Request classification logic
├── retriever.py # BM25 / similarity retrieval
├── responder.py # Response generation
├── escalation.py # Safety + escalation rules
├── product.py # Product area detection
├── utils.py # Helpers + logging
├── safety.py # Safety filters
├── corpus.py # Corpus loading
├── llm.py # (Optional enhancements)
└── inspect_output.py # Output inspection tool
