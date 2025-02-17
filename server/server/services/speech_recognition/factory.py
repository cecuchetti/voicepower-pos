from enum import Enum
from typing import Type
from server.services.speech_recognition.base import SpeechRecognitionService
from server.services.speech_recognition.vosk_service import VoskService

class SpeechRecognitionProvider(str, Enum):
    VOSK = "vosk"
    # Add more providers here as needed
    
def get_speech_recognition_service(provider: SpeechRecognitionProvider) -> Type[SpeechRecognitionService]:
    """Factory method to get speech recognition service."""
    services = {
        SpeechRecognitionProvider.VOSK: VoskService,
        # Add more mappings here as needed
    }
    
    if provider not in services:
        raise ValueError(f"Unsupported speech recognition provider: {provider}")
    
    return services[provider] 