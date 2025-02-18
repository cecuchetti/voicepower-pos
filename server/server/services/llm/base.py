from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMService(ABC):
    """Base abstract class for LLM services"""
    
    @abstractmethod
    async def text_to_shopping_list(self, text: str) -> List[dict]:
        """Convert text to a structured shopping list"""
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generic method for chat completions"""
        pass 