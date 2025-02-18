from typing import Optional
from .base import LLMService
from .providers.openai.gpt35 import GPT35TurboService
from .providers.openai.gpt4 import GPT4Service
from .models import OpenAIModels

class LLMServiceFactory:
    @staticmethod
    def create(provider: str = "openai", model: Optional[str] = None) -> LLMService:
        """
        Create an LLM service instance based on provider and model
        
        Args:
            provider: The LLM provider ("openai", "deepseek", etc)
            model: Optional specific model to use
            
        Returns:
            LLMService: An instance of the appropriate LLM service
        """
        if provider.lower() == "openai":
            if model == OpenAIModels.GPT_4:
                return GPT4Service()
            elif model == OpenAIModels.GPT_4_TURBO:
                # return GPT4TurboService()  # TODO: Implementar
                raise NotImplementedError("GPT-4 Turbo not implemented yet")
            else:
                return GPT35TurboService()  # Default model
        # elif provider.lower() == "deepseek":
        #     return DeepSeekService(model)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}") 