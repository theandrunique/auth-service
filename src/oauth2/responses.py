import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

WEB_MESSAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Authorization Response</title>
</head>
<body>
    <script type="text/javascript" nonce="{nonce}">
        (function(window) {{
            const targetOrigin = "{target_origin}";
            const authorizationResponse = {{
                type: "authorization_response",
                response: {response}
            }};
            const mainWin = (window.opener) ? window.opener : window.parent;
            mainWin.postMessage(authorizationResponse, targetOrigin);
        }})(this);
    </script>
</body>
</html>
"""


@dataclass
class Response:
    content: str
    headers: dict[str, str]


class WebMessage:
    def __init__(self, target_origin: str, state: str | None = None):
        self.target_origin = target_origin
        self.state = state

    def add_error(self, error: str) -> "WebMessage":
        if self.response:
            raise RuntimeError("Response already set")

        self.response = {"error": error, "state": self.state}
        return self

    def add_code(self, code: str) -> "WebMessage":
        if self.response:
            raise RuntimeError("Response already set")

        self.response = {"code": code, "state": self.state}
        return self

    def _get_nonce(self) -> str:
        return secrets.token_hex(16)

    def build(self) -> Response:
        nonce = self._get_nonce()
        if not self.response:
            raise RuntimeError("Response not set")

        content = WEB_MESSAGE_TEMPLATE.format(nonce=nonce, target_origin=self.target_origin, response=self.response)
        return Response(content=content, headers={"Content-Security-Policy": f"default-src 'nonce-{nonce}'"})


class RedirectUri:
    def __init__(self, target_origin: str) -> None:
        self.target_origin = target_origin
        self.fragments = {}
        self.params = {}

    def add_fragment(self, key: str, value: str | None) -> "RedirectUri":
        if value:
            self.fragments[key] = value
        return self

    def add_param(self, key: str, value: str | None) -> "RedirectUri":
        if value:
            self.params[key] = value
        return self

    def build(self) -> str:
        uri = f"{self.target_origin}"
        if self.params:
            uri += f"?{urlencode(self.params)}"
        if self.fragments:
            uri += f"#{urlencode(self.fragments)}"
        return uri
