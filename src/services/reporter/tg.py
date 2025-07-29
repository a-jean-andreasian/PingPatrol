import os
import requests
import threading
from .settings import RETRIES, TIMEOUT


class TelegramReporter:
    def __init__(
        self,
        token,
        chat_id
    ):
        if token is None or chat_id is None:
            raise ValueError("Token or chat id is/are not set")

        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def _payload(self, content: str | bytes, encoding: str = 'utf-8'):
        if isinstance(content, bytes):
            content = content.decode(encoding)

        return {
            "chat_id": self.chat_id,
            "text": content
        }

    def _report(self, content: str | bytes | dict, encoding: str = 'utf-8'):
        payload = self._payload(content, encoding)

        for i in range(RETRIES):
            print(f"[TRY {i}] Sending payload: {payload}")
            try:
                response = requests.post(self.url, data=payload, timeout=TIMEOUT)
                print(f"[TRY {i}] Status: {response.status_code}, Body: {response.text}")
                if response.ok:
                    print('[TRY {i}] Report sent successfully.')
                    break
            except requests.RequestException as e:
                print(f"[TRY {i}] Request failed: {e}")


    def report(self, content: str, encoding: str = 'utf-8'):
        threading.Thread(target=self._report, args=(content, encoding), daemon=True).start()
