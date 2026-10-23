# Support Triage Agent (HackerRank Orchestrate, May 2026)

A rule-based support triage pipeline that classifies tickets, detects the product
area, decides whether to reply or escalate to a human, and returns a response for
**HackerRank, Claude, and Visa** support tickets. Built for the HackerRank
Orchestrate hackathon (ranked 655th).

## How it works

1. **Safety / escalation** (`safety.py`, `escalation.py`): 11 prioritized regex rules
   (fraud, refund/chargeback demands, prompt injection, outages, security reports,
   vendor questionnaires, out-of-scope questions, vague messages) run first and
   escalate sensitive tickets to a human before any reply is generated.
2. **Request classification** (`classifier.py`): keyword rules assign one of
   `product_issue`, `feature_request`, `bug`, `invalid`.
3. **Product area** (`utils.py`): keyword-based area detection.
4. **Response** (`retriever.py`, `responder.py`): TF-IDF cosine-similarity retrieval
   (threshold 0.3) over `data/sample_support_tickets.csv`, with company-specific
   fallback templates when there is no close match.
5. **Output** (`main.py`): a CSV with status, product area, response, justification
   and request type, plus a run log.

`corpus.py` and `llm.py` are optional extensions (support-docs loader and an
Anthropic-API reply composer); they are not used by the default pipeline.

## Setup

    pip install -r requirements.txt

## Run

    python main.py --input data/support_tickets.csv --output output/output.csv

Input CSV columns: `issue`, `subject`, `company`. Retrieval needs
`data/sample_support_tickets.csv` (columns `issue`, `response`); without it the
agent falls back to the templates.

Streamlit demo: `streamlit run app.py`

## Evaluation

Tested on a hand-built set of 30 tickets (10 each for HackerRank, Claude, Visa) in
`data/test_tickets.csv`, with expected request types and reply/escalate decisions.

    python main.py --input data/test_tickets.csv --output output/test_output.csv
    python evaluate.py

| Metric | Result |
|---|---|
| Reply-vs-escalate accuracy | 27/30 (90%) |
| Escalation precision | 9/10 (90%) |
| Escalation recall | 9/11 (82%) |
| Request-type accuracy | 20/30 (67%) |

### Limitations
- The test set was written by me, so these figures are not a benchmark.
- The request-type classifier is keyword-based and misses many simple cases
  (for example, feature requests that do not contain the word "feature").
- The prompt-injection rule treats the word "show" as a trigger and wrongly
  escalated one feature request.
- Retrieval uses TF-IDF over sample tickets, not the full support corpus.

### Next steps
Replace keyword classification with a trained or LLM-based classifier and move
retrieval to BM25 over the support corpus.

## Project structure

    main.py            Batch pipeline (entry point)
    app.py             Streamlit demo
    classifier.py      Request-type rules
    safety.py          Escalation / safety rules
    escalation.py      Reply-vs-escalate decision
    product.py         Legacy product-area helper (unused)
    utils.py           Product area, justification, CSV + logging helpers
    retriever.py       TF-IDF similarity retrieval
    responder.py       Response selection
    corpus.py          Optional support-docs loader
    llm.py             Optional LLM reply composer
    evaluate.py        Scores the pipeline on data/test_tickets.csv
    inspect_output.py  Pretty-prints an output CSV
