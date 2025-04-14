from prodadvert.application.interfaces.ai import TextGenerator, Language
from prodadvert.infrastructure.ai.ddg_client import DuckDuckGoAI


_PROMPTS = {
    Language.EN: "Please, create a short advertisement text about {0}",
    Language.RU: "Пожалуйста, напиши короткий рекламный текст про {0}",
}


class TextGeneratorImpl(TextGenerator):
    def __init__(self):
        self.client = DuckDuckGoAI()

    async def generate_for(
            self,
            topic: str,
            language: Language,
            additional_instructions: str | None = None
    ) -> str:
        await self.client.connect()
        prompt = _PROMPTS[language].format(topic)
        if additional_instructions:
            prompt = prompt + f". {additional_instructions}"
        return await self.client.chat(prompt)
