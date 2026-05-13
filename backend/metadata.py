import logging
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "ReadLater/0.1"
FETCH_TIMEOUT_SECONDS = 10
MAX_REDIRECTS = 5

FAILED_RESULT: dict = {
    "title": None,
    "description": None,
    "image": None,
    "site_name": None,
    "author": None,
    "canonical_url": None,
    "fetch_status": "failed",
}


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _first_meta_content(soup: BeautifulSoup, selectors: list[str]) -> Optional[str]:
    for selector in selectors:
        element = soup.select_one(selector)
        if element is None:
            continue
        value = _clean(element.get("content"))
        if value:
            return value
    return None


def _resolve_url(value: Optional[str], base: str) -> Optional[str]:
    if not value:
        return None
    absolute = urljoin(base, value)
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return absolute


def _build_session() -> requests.Session:
    session = requests.Session()
    session.max_redirects = MAX_REDIRECTS
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def extract_metadata(url: str, session: Optional[requests.Session] = None) -> dict:
    owned_session = session is None
    session = session or _build_session()
    try:
        try:
            response = session.get(
                url,
                timeout=FETCH_TIMEOUT_SECONDS,
                allow_redirects=True,
            )
        except requests.RequestException:
            logger.exception("fetch failed for %s", url)
            return dict(FAILED_RESULT)

        if response.status_code < 200 or response.status_code >= 300:
            logger.info("non-2xx response for %s: %s", url, response.status_code)
            return dict(FAILED_RESULT)

        content_type = response.headers.get("content-type", "").lower()
        is_html = "text/html" in content_type or "application/xhtml+xml" in content_type
        if not is_html:
            logger.info("non-HTML content-type for %s: %s", url, content_type)
            return dict(FAILED_RESULT)

        soup = BeautifulSoup(response.text, "html.parser")
        final_url = str(response.url)

        title = _first_meta_content(
            soup,
            [
                'meta[property="og:title"]',
                'meta[name="twitter:title"]',
            ],
        )
        if not title:
            title_el = soup.find("title")
            if title_el is not None:
                title = _clean(title_el.get_text())

        description = _first_meta_content(
            soup,
            [
                'meta[property="og:description"]',
                'meta[name="twitter:description"]',
                'meta[name="description"]',
            ],
        )

        image = _first_meta_content(
            soup,
            [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
            ],
        )
        image = _resolve_url(image, final_url)

        site_name = _first_meta_content(
            soup,
            ['meta[property="og:site_name"]'],
        )

        author = _first_meta_content(
            soup,
            [
                'meta[name="author"]',
                'meta[property="article:author"]',
            ],
        )

        canonical_url: Optional[str] = None
        canonical_el = soup.select_one('link[rel="canonical"][href]')
        if canonical_el is not None:
            canonical_url = _resolve_url(_clean(canonical_el.get("href")), final_url)

        fetch_status = "ok" if title else "partial"

        return {
            "title": title,
            "description": description,
            "image": image,
            "site_name": site_name,
            "author": author,
            "canonical_url": canonical_url,
            "fetch_status": fetch_status,
        }
    finally:
        if owned_session:
            session.close()
