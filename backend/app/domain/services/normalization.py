import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    value = re.sub(r"\b(pvt|private|limited|ltd|llp)\b", " ", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if not k.lower().startswith(("utm_", "fbclid", "gclid"))))
    return urlunsplit((parts.scheme.lower() or "https", parts.netloc.lower(), parts.path.rstrip("/"), query, ""))

