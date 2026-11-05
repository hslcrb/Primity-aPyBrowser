import pytest

from src.core.navigation import address_to_url, is_web_url, safe_external_url


@pytest.mark.parametrize(("text", "expected"), [
    ("figma.com", "https://figma.com"),
    ("https://figma.com/design?id=1&x=2", "https://figma.com/design?id=1&x=2"),
    ("localhost:3000", "http://localhost:3000"),
    ("127.0.0.1:8080/a", "http://127.0.0.1:8080/a"),
    ("[::1]:3000", "http://[::1]:3000"),
    ("primity://newtab", "primity://newtab"),
])
def test_addresses(text, expected):
    assert address_to_url(text) == expected


def test_search_is_encoded_without_parameter_injection():
    assert address_to_url("피그마 A & B#C") == "https://www.google.com/search?q=%ED%94%BC%EA%B7%B8%EB%A7%88+A+%26+B%23C"


@pytest.mark.parametrize("url", ["javascript:alert(1)", "file:///etc/passwd", "data:text/html,hi", "chrome://settings", "https://user:secret@example.com", "https://", "http://a\nInjected", "https://example.com:bad", "--remote-debugging-port=9222"])
def test_external_url_rejects_unsafe_values(url):
    with pytest.raises(ValueError):
        safe_external_url(url)
    assert not is_web_url(url)


def test_external_url_keeps_query_as_one_value():
    assert safe_external_url("https://example.com/?q=--no-sandbox") == "https://example.com/?q=--no-sandbox"


@pytest.mark.parametrize("text", ["javascript:alert(1)", "file:///tmp/file", "data:text/plain,hi", "https://user:secret@example.com"])
def test_omnibox_rejects_unsupported_schemes(text):
    with pytest.raises(ValueError):
        address_to_url(text)

