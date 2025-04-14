from abc import ABC, abstractmethod
from enum import Enum


class Language(Enum):
    EN = "EN"
    RU = "RU"


class TextGenerator(ABC):
    @abstractmethod
    async def generate_for(
            self,
            topic: str,
            language: Language,
            additional_instructions: str | None = None
    ) -> str:
        """Generate text."""
