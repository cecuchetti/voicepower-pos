from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import json
from pathlib import Path
from .base import LLMService
from .models import OpenAIModels

# Obtener el directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent.parent.parent
ENV_FILE = ROOT_DIR / '.env'

print(f"Intentando cargar .env desde: {ENV_FILE}")
# Cargar .env desde el directorio raíz
loaded = load_dotenv(ENV_FILE)
print(f"Archivo .env cargado: {loaded}")

class OpenAIService(LLMService):
    def __init__(self, model: str = OpenAIModels.GPT_3_5_TURBO):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "No se encontró OPENAI_API_KEY en las variables de entorno. "
                "Asegúrate de que existe y contiene la API key."
            )
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generic method for chat completions"""
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
                        IMPORTANTE: Debes inventar precios razonables en pesos argentinos para cada producto.
                        Devuelve una lista de objetos JSON con este formato exacto:
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
            print(f"OpenAI response: {content}")  # Debug log
            
            try:
                shopping_list = json.loads(content)
                # Validar cada item
                for item in shopping_list:
                    if not all(key in item for key in ["name", "quantity", "unit_price"]):
                        raise ValueError("Missing required fields in item")
                return shopping_list
            except json.JSONDecodeError:
                return self._parse_text_response(content)
                
        except Exception as e:
            print(f"Error processing shopping list: {str(e)}")
            raise
    
    def _parse_text_response(self, content: str) -> List[dict]:
        """Parse non-JSON response into shopping list format"""
        items = []
        for line in content.split('\n'):
            if '-' in line:
                parts = line.split('-')[1].strip().split('x')
                if len(parts) >= 2:
                    quantity = float(parts[0].strip())
                    name_price = parts[1].strip()
                    if '($' in name_price:
                        name, price_str = name_price.split('($')
                        unit_price = float(price_str.split()[0])
                    else:
                        unit_price = 1.0
                    
                    items.append({
                        "name": name.strip(),
                        "quantity": quantity,
                        "unit_price": unit_price
                    })
        return items 