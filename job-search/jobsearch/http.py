"""Tiny JSON-over-HTTP helper (stdlib only)."""

import json
import urllib.error
import urllib.request
from urllib.parse import urlencode

USER_AGENT = "jobsearch/0.1 (personal use)"


class FetchError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def get_json(url: str, params: dict | None = None, timeout: float = 20):
    if params:
        url = f"{url}{'&' if '?' in url else '?'}{urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code}", status=e.code) from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise FetchError(f"network error: {getattr(e, 'reason', e)}") from None
    except json.JSONDecodeError:
        raise FetchError("response was not JSON") from None
