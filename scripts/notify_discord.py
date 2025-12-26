import requests


def notify(webhook_url, message):
    if not webhook_url:
        return
    response = requests.post(webhook_url, json={"content": message}, timeout=30)
    response.raise_for_status()
