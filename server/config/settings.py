from typing import Dict, Any
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings:
    """Application settings for different environments."""
    
    ENVIRONMENTS: Dict[Environment, Dict[str, Any]] = {
        Environment.DEVELOPMENT: {
            "VOSK_SERVER_URI": "ws://localhost:2700",
            "LOG_LEVEL": "DEBUG",
        },
        Environment.PRODUCTION: {
            "VOSK_SERVER_URI": "ws://vosk-server:2700",
            "LOG_LEVEL": "INFO",
        },
        Environment.TESTING: {
            "VOSK_SERVER_URI": "ws://test-server:2700",
            "LOG_LEVEL": "DEBUG",
        }
    }

    @classmethod
    def get_settings(cls, env: Environment = Environment.DEVELOPMENT) -> Dict[str, Any]:
        """Get settings for specific environment."""
        base_config = load_env_config()  # from config.py
        env_config = cls.ENVIRONMENTS[env]
        return {**base_config, **env_config} 