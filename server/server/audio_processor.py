import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import numpy as np
import sounddevice as sd
import websockets
from websockets.exceptions import WebSocketException
from server.config import config
import soundfile as sf
from server.services.speech_recognition.base import SpeechRecognitionService
from server.services.speech_recognition.vosk_service import VoskService

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

@dataclass
class AudioConfig:
    """Configuration for audio processing."""
    uri: str = config.VOSK_SERVER_URI
    device: Optional[int] = None
    samplerate: int = config.AUDIO_SAMPLERATE
    blocksize: int = config.AUDIO_BLOCKSIZE
    channels: int = config.AUDIO_CHANNELS
    timeout: int = config.AUDIO_TIMEOUT
    language: str = config.AUDIO_LANGUAGE
    input_file: Optional[str] = None  # New field for file input

class AudioProcessingError(Exception):
    """Custom exception for audio processing errors."""
    pass

class AudioProcessor:
    """
    Process audio input and convert it to text using a WebSocket service.
    
    Attributes:
        config (AudioConfig): Configuration for audio processing
        audio_queue (asyncio.Queue): Queue for audio data
        text_buffer (List[str]): Buffer for processed text
        last_text_time (float): Timestamp of last received text
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.audio_queue: asyncio.Queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()
        self.text_buffer: List[str] = []
        self.last_text_time: float = time.time()
        self.logger = logging.getLogger(__name__)
        self.speech_service: SpeechRecognitionService = VoskService()

    def callback(self, indata: np.ndarray, frames: int, time_info: Dict, status: Any) -> None:
        """
        Callback function for audio input processing.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Status flags
        """
        if status:
            self.logger.warning(f"Audio input status: {status}")
        
        try:
            audio_data = np.frombuffer(indata, dtype='int16')
            if audio_data.any():
                self.loop.call_soon_threadsafe(self.audio_queue.put_nowait, bytes(indata))
                self.logger.debug("Audio data received")
        except Exception as e:
            self.logger.error(f"Error processing audio input: {e}")

    async def _process_response(self, response: str) -> None:
        """
        Process the response from the WebSocket server.
        
        Args:
            response: JSON response from the server
        """
        try:
            response_data = json.loads(response)
            if "text" in response_data and response_data["text"].strip():
                text = response_data["text"]
                self.logger.info(f"Recognized text: {text}")
                self.text_buffer.append(text)
                self.last_text_time = time.time()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing response: {e}")

    async def _check_timeout(self) -> bool:
        """Check if the processing should timeout."""
        current_time = time.time()
        if current_time - self.last_text_time > self.config.timeout:
            self.logger.info("No text recognized for %d seconds, stopping...", 
                           self.config.timeout)
            return True
        return False

    async def process_audio(self) -> str:
        """Process audio from microphone."""
        stream = None
        last_log_time = time.time()
        self.last_text_time = time.time()  # Reiniciar el tiempo al comenzar
        
        try:
            await self.speech_service.initialize()
            print("Audio processing started. Speak into the microphone...")
            
            # Set up audio stream
            stream = sd.RawInputStream(
                samplerate=self.config.samplerate,
                blocksize=self.config.blocksize,
                device=self.config.device,
                dtype='int16',
                channels=self.config.channels,
                callback=self.callback
            )
            stream.start()
            
            async def audio_generator():
                while True:
                    try:
                        data = await asyncio.wait_for(
                            self.audio_queue.get(), 
                            timeout=1.0
                        )
                        yield data
                    except asyncio.TimeoutError:
                        current_time = time.time()
                        if current_time - self.last_text_time > self.config.timeout:
                            print(f"No text recognized for {self.config.timeout} seconds, stopping...")
                            break
                        continue
            
            # Process audio stream
            async for result in self.speech_service.process_audio_stream(audio_generator()):
                current_time = time.time()
                
                # Actualizar el tiempo si hay actividad de voz
                if result["has_voice_activity"]:
                    self.last_text_time = current_time
                
                # Agregar texto si existe
                if result["text"]:
                    print(f"Recognized text: {result['text']}")
                    self.text_buffer.append(result["text"])
                elif current_time - last_log_time > 5:
                    print("Listening...")
                    last_log_time = current_time
                
                # Verificar timeout
                if current_time - self.last_text_time > self.config.timeout:
                    print(f"No voice activity for {self.config.timeout} seconds, stopping...")
                    break
            
            return " ".join(self.text_buffer)
            
        finally:
            if stream and stream.active:
                stream.stop()
                stream.close()
            await self.speech_service.shutdown()

    async def process_audio_file(self) -> str:
        """Process audio from file."""
        try:
            await self.speech_service.initialize()
            text = await self.speech_service.process_audio_file(self.config.input_file)
            return text
        finally:
            await self.speech_service.shutdown()

# Example usage:
if __name__ == "__main__":
    config = AudioConfig(
        uri='ws://localhost:2700',
        language='es',
        timeout=30
    )
    processor = AudioProcessor(config)
    text = asyncio.run(processor.process_audio())
    print(f"Processed text: {text}") 