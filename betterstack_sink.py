import urllib.request
import json
import ssl
from datetime import timezone


class BetterStackSink:
    def __init__(self, token: str, url: str):
        self.token = token
        self.url = url.rstrip("/")
        # BetterStack may use self-signed or mismatched cert — skip verification
        self._ssl_ctx = ssl.create_default_context()
        self._ssl_ctx.check_hostname = False
        self._ssl_ctx.verify_mode = ssl.CERT_NONE

    def __call__(self, message):
        record = message.record
        payload = json.dumps({
            "dt": record["time"].astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "message": record["message"],
            "level": record["level"].name,
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }).encode()

        req = urllib.request.Request(
            self.url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=5):
                pass
        except Exception:
            pass  # never let logging break the app
