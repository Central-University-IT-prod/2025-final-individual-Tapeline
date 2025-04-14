import aiohttp

from prodadvert_bot.application.interfaces.text_generator import TextGenerator
from prodadvert_bot.config import Config


class TextGeneratorImpl(TextGenerator):
    def __init__(self, config: Config) -> None:
        self.base_url = config.api.base_url

    async def generate(
            self, topic: str, lang: str, additional: str
    ) -> str | None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/ai/generate-text",
                json={
                    "language": lang,
                    "topic": topic,
                    "additional": additional
                }
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return data["result"]
