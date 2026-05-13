from unittest.mock import MagicMock, patch

import requests

from backend.metadata import extract_metadata

HTML_FULL = """
<!doctype html>
<html>
<head>
  <title>Fallback Title</title>
  <link rel="canonical" href="/canonical-path">
  <meta property="og:title" content="OG Title">
  <meta property="og:description" content="OG Description">
  <meta property="og:image" content="/img/cover.jpg">
  <meta property="og:site_name" content="Example Site">
  <meta name="author" content="Jane Doe">
</head>
<body><p>hello</p></body>
</html>
"""

HTML_TITLE_ONLY = """
<!doctype html>
<html>
<head>
  <title>   Just A Title   </title>
  <meta name="description" content="  Desc fallback ">
</head>
</html>
"""

HTML_NO_TITLE = """
<!doctype html>
<html>
<head>
  <meta name="description" content="No title here">
</head>
</html>
"""


def _mock_response(text: str, status: int = 200, url: str = "https://example.com/article", content_type: str = "text/html; charset=utf-8"):
    response = MagicMock(spec=requests.Response)
    response.text = text
    response.status_code = status
    response.url = url
    response.headers = {"content-type": content_type}
    return response


def _patched_session(response):
    session = MagicMock(spec=requests.Session)
    session.get.return_value = response
    session.close = MagicMock()
    return session


def test_extract_full_metadata():
    response = _mock_response(HTML_FULL)
    session = _patched_session(response)
    result = extract_metadata("https://example.com/article", session=session)

    assert result["fetch_status"] == "ok"
    assert result["title"] == "OG Title"
    assert result["description"] == "OG Description"
    assert result["image"] == "https://example.com/img/cover.jpg"
    assert result["site_name"] == "Example Site"
    assert result["author"] == "Jane Doe"
    assert result["canonical_url"] == "https://example.com/canonical-path"


def test_extract_title_fallback_to_title_tag():
    response = _mock_response(HTML_TITLE_ONLY)
    session = _patched_session(response)
    result = extract_metadata("https://example.com/article", session=session)

    assert result["fetch_status"] == "ok"
    assert result["title"] == "Just A Title"
    assert result["description"] == "Desc fallback"
    assert result["image"] is None
    assert result["canonical_url"] is None


def test_partial_when_no_title_present():
    response = _mock_response(HTML_NO_TITLE)
    session = _patched_session(response)
    result = extract_metadata("https://example.com/article", session=session)

    assert result["fetch_status"] == "partial"
    assert result["title"] is None
    assert result["description"] == "No title here"


def test_failed_on_request_exception():
    session = MagicMock(spec=requests.Session)
    session.get.side_effect = requests.ConnectionError("boom")
    session.close = MagicMock()

    result = extract_metadata("https://example.com/article", session=session)

    assert result["fetch_status"] == "failed"
    assert result["title"] is None
    assert result["description"] is None


def test_failed_on_non_2xx():
    response = _mock_response("oops", status=500)
    session = _patched_session(response)
    result = extract_metadata("https://example.com/article", session=session)

    assert result["fetch_status"] == "failed"


def test_failed_on_non_html_content_type():
    response = _mock_response("{}", content_type="application/json")
    session = _patched_session(response)
    result = extract_metadata("https://example.com/article", session=session)

    assert result["fetch_status"] == "failed"


def test_relative_canonical_resolved_against_final_url():
    response = _mock_response(HTML_FULL, url="https://example.com/articles/index")
    session = _patched_session(response)
    result = extract_metadata("https://example.com/articles/index", session=session)

    assert result["canonical_url"] == "https://example.com/canonical-path"
    assert result["image"] == "https://example.com/img/cover.jpg"
