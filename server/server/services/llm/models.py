class OpenAIModels:
    """Constants for OpenAI model names"""
    # Chat models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Vision models
    GPT_4_VISION = "gpt-4-vision-preview"
    
    # Audio models
    WHISPER = "whisper-1"
    
    # Image models
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    
    # Embedding models
    EMBEDDING_3_LARGE = "text-embedding-3-large"
    EMBEDDING_3_SMALL = "text-embedding-3-small"
    
    @classmethod
    def is_vision_model(cls, model: str) -> bool:
        return model == cls.GPT_4_VISION
    
    @classmethod
    def is_chat_model(cls, model: str) -> bool:
        return model in [cls.GPT_4, cls.GPT_4_TURBO, cls.GPT_3_5_TURBO]

class DeepSeekModels:
    """Constants for DeepSeek model names"""
    # Add DeepSeek models here when implementing
    pass 