import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass

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


@dataclass
class WebMessage(ABC):
    target_origin: str
    state: str | None

    @abstractmethod
    def build(self) -> Response: ...

    def _get_nonce(self) -> str:
        return secrets.token_hex(16)

    def _build_response(self, response: dict) -> Response:
        nonce = self._get_nonce()
        content = WEB_MESSAGE_TEMPLATE.format(nonce=nonce, target_origin=self.target_origin, response=response)
        return Response(content=content, headers={"Content-Security-Policy": f"default-src 'nonce-{nonce}'"})


@dataclass
class WebMessageError(WebMessage):
    error: str

    def build(self) -> Response:
        response = {"error": self.error, "state": self.state}
        return self._build_response(response)


@dataclass
class WebMessageSuccess(WebMessage):
    code: str

    def build(self) -> Response:
        response = {"code": self.code, "state": self.state}
        return self._build_response(response)


@dataclass
class RedirectUri(ABC):
    target_origin: str
    state: str | None

    @abstractmethod
    def build(self) -> str: ...


@dataclass
class RedirectUriSuccessToken(RedirectUri):
    access_token: str
    expires_in: int
    token_type: str = "Bearer"

    def build(self) -> str:
        return (
            f"{self.target_origin}#access_token={self.access_token}"
            f"&expires_in={self.expires_in}"
            f"&token_type={self.token_type}"
            f"&state={self.state}"
        )


@dataclass
class RedirectUriSuccess(RedirectUri):
    code: str

    def build(self) -> str:
        return f"{self.target_origin}?code={self.code}&state={self.state}"


@dataclass
class RedirectUriError(RedirectUri):
    error: str

    def build(self) -> str:
        return f"{self.target_origin}?error={self.error}&state={self.state}"
