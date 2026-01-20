# Human-in-the-Loop Validation System (Prototype)

This prototype shows how to route classification requests between an AI model
and human reviewers. High-confidence predictions are returned immediately.
Low-confidence cases are queued for human labeling, and the final decision is
aggregated by a Strategy (Majority Vote).

## Why this matters for web scraping

In webscraping services, some data is hard to parse programmatically. Examples
include complex CAPTCHAs, niche product categorization, or low-quality text in
scanned documents. A Human-in-the-Loop flow allows automatic extraction to run
fast while routing ambiguous cases to humans for verification.

## API Overview

### POST /classify

```
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"good excellent amazing\"}"
```

### GET /tasks/{task_id}

```
curl http://127.0.0.1:8000/tasks/{task_id}
```

### POST /tasks/{task_id}/label

```
curl -X POST http://127.0.0.1:8000/tasks/{task_id}/label \
  -H "Content-Type: application/json" \
  -d "{\"label\": \"positive\", \"worker_id\": \"w1\"}"
```

## Setup

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests

```
pytest
```
