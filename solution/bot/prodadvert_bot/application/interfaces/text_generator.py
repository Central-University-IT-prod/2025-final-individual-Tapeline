from abc import ABC, abstractmethod


class TextGenerator(ABC):
    @abstractmethod
    async def generate(
            self, topic: str, lang: str, additional: str
    ) -> str | None:
        """Generate text with AI."""
