
import aiohttp
import json

_STATUS_URL = "https://duckduckgo.com/duckchat/v1/status"
_CHAT_URL = "https://duckduckgo.com/duckchat/v1/chat"
_DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


class DuckDuckGoAI:
    def __init__(
            self,
            model: str = _DEFAULT_MODEL
    ) -> None:
        self.model = model
        self.vqd: str | None = None

    async def connect(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                _STATUS_URL,
                headers={
                    "x-vqd-accept": "1"
                },
            ) as response:
                self.vqd = response.headers["x-vqd-4"]

    async def chat(self, prompt: str) -> str:
        if self.vqd is None:  # pragma: no cover
            raise ValueError("Not connected")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _CHAT_URL,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                headers={
                    "x-vqd-4": self.vqd
                },
            ) as response:
                resp = await response.text()
                text = ""
                for message in resp.split("\n\n"):
                    text += self._decode(message)
                return text

    def _decode(self, message: str) -> str:
        if len(message.strip()) < 1:
            return ""
        message = message.removeprefix("data: ").strip()
        if message == "[DONE]":
            return ""
        json_data = json.loads(message)
        return json_data.get("message", "")
