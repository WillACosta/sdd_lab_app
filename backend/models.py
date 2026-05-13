from typing import Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator

FetchStatus = Literal["ok", "partial", "failed"]


class CreateItemRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("URL must not be empty")
        parsed = urlparse(stripped)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https scheme")
        if not parsed.netloc:
            raise ValueError("URL must include a host")
        return stripped


class Item(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    url: str
    canonical_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    site_name: Optional[str] = None
    author: Optional[str] = None
    created_at: str
    fetch_status: FetchStatus
