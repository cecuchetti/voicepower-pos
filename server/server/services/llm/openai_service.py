from openai import AsyncOpenAI
from typing import List
import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Obtener el directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent.parent.parent
ENV_FILE = ROOT_DIR / '.env'

print(f"Intentando cargar .env desde: {ENV_FILE}")
# Cargar .env desde el directorio raíz
loaded = load_dotenv(ENV_FILE)
print(f"Archivo .env cargado: {loaded}")

class OpenAIService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"API Key encontrada: {'Sí' if api_key else 'No'}")
        if not api_key:
            raise ValueError(
                f"No se encontró OPENAI_API_KEY en {ENV_FILE}. "
                "Asegúrate de que el archivo .env existe y contiene la API key."
            )
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    async def text_to_shopping_list(self, text: str) -> List[dict]:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
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
                        Por ejemplo:
                        [
                            {
                                "name": "queso",
                                "quantity": 200,
                                "unit_price": 2500
                            },
                            {
                                "name": "empanada",
                                "quantity": 1,
                                "unit_price": 500
                            }
                        ]
                        
                        Asegúrate de:
                        1. Siempre incluir un precio inventado pero realista para cada producto
                        2. Los precios deben ser números, no null ni strings
                        3. Usar precios actuales aproximados del mercado argentino
                    """},
                    {"role": "user", "content": text}
                ]
            )
            
            # Extraer y validar la respuesta
            content = response.choices[0].message.content
            print(f"OpenAI response: {content}")  # Debug log
            
            try:
                shopping_list = json.loads(content)
                # Validar cada item
                for item in shopping_list:
                    if not all(key in item for key in ["name", "quantity", "unit_price"]):
                        raise ValueError("Missing required fields in item")
                return shopping_list
            except json.JSONDecodeError:
                # Si la respuesta no es JSON válido, intentar parsear el texto
                items = []
                for line in content.split('\n'):
                    if '-' in line:
                        parts = line.split('-')[1].strip().split('x')
                        if len(parts) >= 2:
                            quantity = float(parts[0].strip())
                            name_price = parts[1].strip()
                            # Extraer precio si está presente
                            if '($' in name_price:
                                name, price_str = name_price.split('($')
                                unit_price = float(price_str.split()[0])
                            else:
                                unit_price = 1.0  # precio por defecto
                            
                            items.append({
                                "name": name.strip(),
                                "quantity": quantity,
                                "unit_price": unit_price
                            })
                return items
                
        except Exception as e:
            print(f"Error processing shopping list: {str(e)}")
            raise 