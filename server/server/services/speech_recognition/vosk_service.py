import json
import asyncio
from typing import Optional, AsyncGenerator
import websockets
from server.services.speech_recognition.base import SpeechRecognitionService
from server.config import config
import time

class VoskService(SpeechRecognitionService):
    """VOSK implementation of speech recognition service."""
    
    def __init__(self, uri: str = config.VOSK_SERVER_URI, language: str = config.AUDIO_LANGUAGE):
        self.uri = uri
        self.language = language
        self.websocket = None
    
    async def initialize(self) -> None:
        """Initialize connection to VOSK server."""
        try:
            print(f"Connecting to VOSK server at {self.uri}...")
            self.websocket = await websockets.connect(self.uri)
            config_msg = {
                "config": {
                    "sample_rate": config.AUDIO_SAMPLERATE,
                    "lang": self.language
                }
            }
            print(f"Sending config: {config_msg}")
            await self.websocket.send(json.dumps(config_msg))
            print("VOSK server initialized successfully")
        except Exception as e:
            print(f"Error initializing VOSK server: {e}")
            raise
    
    async def process_audio_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Process streaming audio data using VOSK."""
        try:
            print("Starting audio stream processing...")
            async for chunk in audio_stream:
                await self.websocket.send(chunk)
                response = await self.websocket.recv()
                response_data = json.loads(response)
                
                # Yield tanto el texto como un indicador de actividad de voz
                has_voice_activity = False
                text = ""
                
                if "text" in response_data and response_data["text"].strip():
                    text = response_data["text"].strip()
                    has_voice_activity = True
                elif "partial" in response_data and response_data["partial"].strip():
                    has_voice_activity = True
                
                yield {
                    "text": text,
                    "has_voice_activity": has_voice_activity
                }
                    
            print("Audio stream ended, sending EOF")
            await self.websocket.send('{"eof" : 1}')
            final_response = await self.websocket.recv()
            response_data = json.loads(final_response)
            if "text" in response_data and response_data["text"].strip():
                yield {
                    "text": response_data["text"].strip(),
                    "has_voice_activity": True
                }
                
        except Exception as e:
            print(f"Error in audio stream processing: {e}")
            raise RuntimeError(f"Error processing audio stream: {e}")
    
    async def process_audio_file(self, file_path: str) -> str:
        """Process audio file using VOSK."""
        import soundfile as sf
        
        try:
            audio_data, sample_rate = sf.read(file_path)
            texts = []
            
            chunk_size = config.AUDIO_BLOCKSIZE
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                await self.websocket.send(bytes(chunk))
                response = await self.websocket.recv()
                response_data = json.loads(response)
                if "text" in response_data and response_data["text"].strip():
                    texts.append(response_data["text"])
            
            return " ".join(texts)
            
        except Exception as e:
            raise RuntimeError(f"Error processing audio file: {e}")
    
    async def shutdown(self) -> None:
        """Close connection to VOSK server."""
        if self.websocket:
            await self.websocket.close() 