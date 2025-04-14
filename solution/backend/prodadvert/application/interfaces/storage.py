from abc import ABC, abstractmethod


class FileStorage(ABC):
    @abstractmethod
    async def upload_file(
            self, filename: str, content: bytes, content_type: str
    ) -> str:
        """Upload file and get URI."""
