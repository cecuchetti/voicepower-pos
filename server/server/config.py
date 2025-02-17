import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Try to load from root directory

def get_env_var(key: str, default: Any) -> Any:
    """Get environment variable with type conversion."""
    value = os.getenv(key)
    if value is None:
        return default
    
    # Try to convert to the same type as the default value
    try:
        if isinstance(default, bool):
            return value.lower() in ('true', '1', 'yes')
        return type(default)(value)
    except ValueError:
        return value

class Config:
    """Application configuration from environment variables."""
    VOSK_SERVER_URI: str = get_env_var("VOSK_SERVER_URI", "ws://localhost:2700")
    AUDIO_SAMPLERATE: int = get_env_var("AUDIO_SAMPLERATE", 16000)
    AUDIO_BLOCKSIZE: int = get_env_var("AUDIO_BLOCKSIZE", 4000)
    AUDIO_CHANNELS: int = get_env_var("AUDIO_CHANNELS", 1)
    AUDIO_TIMEOUT: int = get_env_var("AUDIO_TIMEOUT", 30)
    AUDIO_LANGUAGE: str = get_env_var("AUDIO_LANGUAGE", "es")
    LOG_LEVEL: str = get_env_var("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = get_env_var(
        "LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

# Create a single instance of Config
config = Config() 