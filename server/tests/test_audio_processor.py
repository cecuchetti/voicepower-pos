import asyncio
from server.audio_processor import AudioProcessor, AudioConfig
from server.services.speech_recognition.factory import get_speech_recognition_service, SpeechRecognitionProvider

async def main():
    """Test the audio processing functionality."""
    try:
        # Get the speech recognition service from factory
        service_class = get_speech_recognition_service(SpeechRecognitionProvider.VOSK)
        
        # Create configuration
        config = AudioConfig(
            uri='ws://localhost:2700',
            device=None,
            samplerate=16000,
            language='es',
            timeout=10  # Reducir el timeout para pruebas
        )
        
        # Create audio processor with the configuration
        processor = AudioProcessor(config)
        
        print("Starting audio processing... (speak into your microphone)")
        print("Processing will stop after 30 seconds of silence")
        
        # Process audio and get the text
        final_text = await processor.process_audio()
        print(f"\nFinal text from audio: {final_text}")
        
    except Exception as e:
        print(f"Error during audio processing: {e}")

if __name__ == '__main__':
    asyncio.run(main()) 