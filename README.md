# ReadLater

A minimal personal read-it-later app. Paste a URL, the backend fetches the page and extracts Open Graph / Twitter Card / standard `<meta>` tags, and the result is stored in a local JSON file. A second page lists everything saved so far.

No accounts, no sync, no editing — see [`spec.md`](spec.md) for the full requirements.

## Stack

- **Frontend** — Streamlit
- **Backend** — FastAPI (Uvicorn)
- **Metadata** — `requests` + BeautifulSoup
- **Storage** — TinyDB (single JSON file at `backend/data/items.json`)

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Run

Open two terminals from the project root:

```bash
# Terminal 1 — backend on http://localhost:8000
.venv/bin/uvicorn backend.main:app --reload
```

```bash
# Terminal 2 — frontend on http://localhost:8501
.venv/bin/streamlit run frontend/app.py
```

The frontend reads `BACKEND_URL` (default `http://localhost:8000`) and the backend reads `DB_PATH` (default `backend/data/items.json`).

## Test

```bash
.venv/bin/pytest
```
