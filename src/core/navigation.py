"""주소창과 외부 브라우저의 URL 경계. / URL boundaries for navigation."""

import ipaddress
import re
from urllib.parse import quote_plus, urlsplit

NEW_TAB = "primity://newtab"
MAX_URL_LENGTH = 8192


def safe_external_url(value: str) -> str:
    """HTTP(S)만 전달한다. / Pass only validated HTTP(S) URLs."""
    if not isinstance(value, str) or not value or len(value) > MAX_URL_LENGTH:
        raise ValueError("올바른 웹 주소를 입력하세요. / Invalid web address.")
    if any(ord(char) < 32 or ord(char) == 127 for char in value) or "\\" in value:
        raise ValueError("주소에 허용되지 않는 문자가 있습니다. / Invalid URL characters.")
    try:
        value.encode("utf-8")
        parsed = urlsplit(value)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or any(char.isspace() for char in value)
                or parsed.port == 0):
            raise ValueError
        if any(char in parsed.hostname for char in "<>'\"%"):
            raise ValueError
        parsed.port  # 잘못된 포트를 검증한다. / Validate malformed ports.
    except (ValueError, UnicodeError) as error:
        raise ValueError("HTTP/HTTPS 주소만 지원합니다. / Only HTTP(S) addresses are supported.") from error
    return value


def is_web_url(value: str) -> bool:
    try:
        safe_external_url(value)
        return True
    except (ValueError, TypeError):
        return False


def address_to_url(value: str) -> str:
    """검색어는 인코딩하고 로컬 개발 주소는 인식한다. / Encode search queries."""
    if not isinstance(value, str) or len(value) > MAX_URL_LENGTH:
        raise ValueError("주소가 너무 깁니다. / Address is too long.")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("주소에 제어 문자를 사용할 수 없습니다. / Control characters are not allowed.")
    value = value.strip()
    if not value or value == NEW_TAB:
        return NEW_TAB
    if value == "about:blank":
        return value
    if value.startswith("//"):
        return safe_external_url("https:" + value)
    if "://" in value:
        return safe_external_url(value)
    if not any(char.isspace() for char in value):
        candidate = urlsplit("//" + value)
        host = candidate.hostname or ""
        loopback = host.lower() == "localhost" or host.lower().endswith(".localhost")
        ip_literal = False
        try:
            address = ipaddress.ip_address(host)
            ip_literal = True
            loopback = loopback or address.is_loopback
        except ValueError:
            pass
        if loopback:
            return safe_external_url("http://" + value)
        if ip_literal or ("." in host and (":" not in value or candidate.port is not None)):
            return safe_external_url("https://" + value)
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        return safe_external_url(value)
    if "." in value and not any(char.isspace() for char in value):
        return safe_external_url("https://" + value)
    return "https://www.google.com/search?q=" + quote_plus(value)

