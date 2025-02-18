from typing import Dict, List, Any, Optional
from ...base import LLMService
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Get project root directory
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent.parent
ENV_FILE = ROOT_DIR / '.env'

print(f"Trying to load .env from: {ENV_FILE}")
# Load .env from root directory
loaded = load_dotenv(ENV_FILE)
print(f".env file loaded: {loaded}")

class BaseOpenAIService(LLMService):
    """Base class for OpenAI services with common functionality"""
    
    def __init__(self, model: str):
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"API Key found: {'Yes' if api_key else 'No'}")
        if not api_key:
            raise ValueError(
                f"No OPENAI_API_KEY found in {ENV_FILE}. "
                "Make sure the .env file exists and contains the API key."
            )
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
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