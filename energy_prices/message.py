import requests
from django.conf import settings


def message(s: str):
    if settings.SLACK_WEBHOOK_URL:
        requests.post(url=settings.SLACK_WEBHOOK_URL, json=dict(text=s))
