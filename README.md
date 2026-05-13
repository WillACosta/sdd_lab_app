# ReadLater

A minimal personal read-it-later app. Paste a URL, and the backend fetches the page to extract Open Graph, Twitter Card, and standard `<meta>` tags. The results are then stored in a local JSON file. A second page lists everything saved so far.

No accounts, no sync, no editing — see [`spec.md`](spec.md) for the full requirements.

![Showcase App Image](./docs/showcase.png)

## Stack

- **Frontend** — Streamlit
- **Backend** — FastAPI (Uvicorn)
- **Metadata** — `requests` + BeautifulSoup
- **Storage** — TinyDB (single JSON file at `backend/data/items.json`)

## Setup & Run

It's recommended to use `make` to simplify the setup and execution process:

> Execute the following command in the root directory:

```shell
make run
```

The frontend reads `BACKEND_URL` (default `http://localhost:8000`) and the backend reads `DB_PATH` (default `backend/data/items.json`).

> Find more details in the `Makefile`
