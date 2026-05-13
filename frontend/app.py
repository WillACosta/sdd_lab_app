import os

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
HTTP_TIMEOUT_SECONDS = 11

st.set_page_config(page_title="ReadLater", page_icon=":books:")
st.title("Save a URL")
st.caption("Paste a URL and press Enter or click Save.")

if st.session_state.pop("_clear_url", False):
    st.session_state["url_input"] = ""

pending = st.session_state.pop("_pending_message", None)
if pending:
    severity, message = pending
    getattr(st, severity)(message)

with st.form("add_url_form", clear_on_submit=False):
    url_value = st.text_input(
        "URL",
        key="url_input",
        placeholder="https://example.com/article",
    )
    submitted = st.form_submit_button("Save", type="primary")


def _post(url: str) -> None:
    try:
        response = requests.post(
            f"{BACKEND_URL}/items",
            json={"url": url},
            timeout=HTTP_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        st.error("Could not reach backend")
        return

    if response.status_code == 201:
        item = response.json()
        status = item.get("fetch_status")
        if status == "ok":
            title = item.get("title") or url
            st.session_state["_pending_message"] = ("success", f"Saved: {title}")
        elif status == "partial":
            st.session_state["_pending_message"] = (
                "info",
                f"Saved (partial metadata): {url}",
            )
        else:
            st.session_state["_pending_message"] = (
                "warning",
                f"Saved without metadata: {url}",
            )
        st.session_state["_clear_url"] = True
        st.rerun()
        return

    if response.status_code == 422:
        try:
            detail = response.json().get("detail", "Invalid URL")
        except ValueError:
            detail = "Invalid URL"
        st.error(detail)
        return

    st.error("Backend error, please try again")


if submitted:
    trimmed = (url_value or "").strip()
    if not trimmed:
        st.error("Please enter a URL")
    else:
        _post(trimmed)
