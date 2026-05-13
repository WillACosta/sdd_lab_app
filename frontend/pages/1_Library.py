import os
from urllib.parse import quote

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
HTTP_TIMEOUT_SECONDS = 11
DESCRIPTION_LIMIT = 280
URL_SAFE_CHARS = ":/?#[]@!$&'()*+,;=~"

st.set_page_config(page_title="Library — ReadLater", page_icon=":books:")
st.title("Your Library")


def _escape_md(text: str) -> str:
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _safe_url(url: str) -> str:
    return quote(url, safe=URL_SAFE_CHARS)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


header_cols = st.columns([6, 1])
with header_cols[1]:
    if st.button("Refresh"):
        st.rerun()

try:
    response = requests.get(f"{BACKEND_URL}/items", timeout=HTTP_TIMEOUT_SECONDS)
except requests.RequestException:
    st.error("Could not reach backend")
    st.stop()

if response.status_code != 200:
    st.error("Backend error, please try again")
    st.stop()

items = response.json()

if not items:
    st.info("No saved URLs yet. Head to the Save a URL page to add your first.")
    st.stop()

for item in items:
    url = item.get("url", "")
    title = item.get("title") or url
    description = item.get("description") or ""
    site_name = item.get("site_name")
    created_at = item.get("created_at", "")
    image = item.get("image")

    with st.container(border=True):
        if image:
            cols = st.columns([1, 4])
            with cols[0]:
                try:
                    st.image(image, use_container_width=True)
                except Exception:
                    pass
            body = cols[1]
        else:
            body = st.container()

        with body:
            st.markdown(f"### [{_escape_md(title)}](<{_safe_url(url)}>)")
            if description:
                st.write(_truncate(description, DESCRIPTION_LIMIT))
            caption_bits = []
            if site_name:
                caption_bits.append(site_name)
            if created_at:
                caption_bits.append(created_at)
            if caption_bits:
                st.caption(" · ".join(caption_bits))
