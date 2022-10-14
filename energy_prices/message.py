import requests
from django.conf import settings


class MessageQueue:
    queue = []

    def message(self, s: str, immediate=None):
        self.queue.append(s)
        if immediate:
            self.flush()

    def flush(self):
        msg = "\n".join(self.queue)
        self.queue = []
        if settings.SLACK_WEBHOOK_URL:
            requests.post(url=settings.SLACK_WEBHOOK_URL, json=dict(text=msg))


messages = MessageQueue()

