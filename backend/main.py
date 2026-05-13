import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.metadata import extract_metadata
from backend.models import CreateItemRequest, Item
from backend.storage import Storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("readlater")

app = FastAPI(title="ReadLater")
storage = Storage()


def _flatten_validation_message(errors: list[dict]) -> str:
    if not errors:
        return "Invalid request"
    msg = str(errors[0].get("msg", "Invalid request"))
    prefix = "Value error, "
    if msg.startswith(prefix):
        msg = msg[len(prefix):]
    return msg


@app.exception_handler(RequestValidationError)
async def _validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    detail = _flatten_validation_message(exc.errors())
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(ValueError)
async def _value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.post("/items", status_code=201, response_model=Item)
async def create_item(body: CreateItemRequest) -> Item:
    started = time.monotonic()
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    meta = extract_metadata(body.url)
    item = Item(
        id=str(uuid.uuid4()),
        url=body.url,
        canonical_url=meta.get("canonical_url"),
        title=meta.get("title"),
        description=meta.get("description"),
        image=meta.get("image"),
        site_name=meta.get("site_name"),
        author=meta.get("author"),
        created_at=created_at,
        fetch_status=meta["fetch_status"],
    )
    storage.insert(item.model_dump())
    duration = time.monotonic() - started
    logger.info(
        "POST /items url=%s status=%s duration=%.2fs",
        body.url,
        item.fetch_status,
        duration,
    )
    return item


@app.get("/items", response_model=list[Item])
async def list_items() -> list[Item]:
    items = storage.list_all()
    return [Item(**item) for item in items]


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}
