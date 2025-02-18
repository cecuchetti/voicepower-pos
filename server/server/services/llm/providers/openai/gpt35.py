from typing import Dict, List, Any, Optional
import json
from .base import BaseOpenAIService
from ...models import OpenAIModels

class GPT35TurboService(BaseOpenAIService):
    """Implementation for GPT-3.5 Turbo model"""
    
    def __init__(self):
        super().__init__(OpenAIModels.GPT_3_5_TURBO)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """GPT-3.5 specific chat completion implementation"""
        response = await self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": response.usage
        }
    
    async def text_to_shopping_list(self, text: str) -> List[dict]:
        try:
            response = await self.chat_completion(
                messages=[
                    {"role": "system", "content": """
                        Convierte el texto en una lista de compras estructurada.
                        IMPORTANTE: 
                        1. Debes inventar precios razonables en pesos argentinos para cada producto.
                        2. Devuelve SOLO el JSON sin formato markdown ni texto adicional.
                        
                        Formato requerido:
                        [
                            {
                                "name": "nombre del producto",
                                "quantity": cantidad numérica,
                                "unit_price": precio inventado en pesos (número)
                            }
                        ]
                    """},
                    {"role": "user", "content": text}
                ]
            )
            
            content = response["content"]
            print(f"OpenAI response: {content}")
            
            # Clean the response from markdown formatting
            content = content.strip()
            if content.startswith("```"):
                # Remove opening ```json or ``` and closing ```
                content = content.split("\n", 1)[1]  # Remove first line
                content = content.rsplit("\n", 1)[0]  # Remove last line
                if content.lower().startswith("json"):
                    content = content[4:].strip()
            
            try:
                shopping_list = json.loads(content)
                # Validate each item
                for item in shopping_list:
                    if not all(key in item for key in ["name", "quantity", "unit_price"]):
                        raise ValueError("Missing required fields in item")
                return shopping_list
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                return self._parse_text_response(content)
                
        except Exception as e:
            print(f"Error processing shopping list: {str(e)}")
            raise 