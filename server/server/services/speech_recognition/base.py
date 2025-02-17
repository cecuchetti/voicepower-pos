from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator

class SpeechRecognitionService(ABC):
    """Abstract base class for speech recognition services."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def process_audio_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Process streaming audio data."""
        pass
    
    @abstractmethod
    async def process_audio_file(self, file_path: str) -> str:
        """Process audio from a file."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up resources."""
        pass 