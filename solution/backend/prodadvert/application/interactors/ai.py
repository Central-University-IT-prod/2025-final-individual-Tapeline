from dishka import FromDishka

from prodadvert.application.interfaces.ai import TextGenerator, Language


class TextGenerationInteractor:
    def __init__(self, generator: FromDishka[TextGenerator]):
        self.generator = generator

    async def __call__(
            self, topic: str, language: Language, additional: str | None
    ) -> str:
        return await self.generator.generate_for(topic, language, additional)
