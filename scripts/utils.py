import time
from typing import Callable

import requests


def request_with_retry(
    method: str,
    url: str,
    headers=None,
    json_payload=None,
    timeout=60,
    max_retries=2,
):
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=json_payload,
                timeout=timeout,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            time.sleep(2 + attempt * 2)
    raise last_exc


def retry_call(fn: Callable, max_retries=2):
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            time.sleep(2 + attempt * 2)
    raise last_exc
