from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import tempfile
import os
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from server.audio_processor import AudioProcessor, AudioConfig, AudioProcessingError
from server.config import config  # Actualizado

app = FastAPI(title="Voice POS API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str
    stock: int

class SaleItem(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class Sale(BaseModel):
    items: List[SaleItem]
    total: float
    date: datetime = datetime.now()
    notes: Optional[str] = None

# Global audio processor instance
audio_processor = AudioProcessor()

@app.post("/audio/process")
async def process_audio(audio_file: UploadFile = File(...)):
    """
    Process an audio file and return recognized text.
    
    Args:
        audio_file: Uploaded audio file (supports wav, mp3, etc.)
        
    Returns:
        dict: Contains recognized text and status
    """
    try:
        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            # Write the uploaded file content to the temporary file
            content = await audio_file.read()
            temp_audio.write(content)
            temp_audio.flush()
            
            # Configure audio processor for file input
            config = AudioConfig(
                uri=app.state.config.VOSK_SERVER_URI,
                input_file=temp_audio.name
            )
            
            # Process the audio file
            processor = AudioProcessor(config)
            text = await processor.process_audio_file()
            
            return {
                "text": text,
                "status": "success",
                "filename": audio_file.filename
            }
            
    except AudioProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if 'temp_audio' in locals():
            os.unlink(temp_audio.name)

@app.get("/products", response_model=List[Product])
async def get_products():
    """
    Return list of available products.
    """
    # TODO: Implement database logic
    # For now, return example data
    products = [
        Product(
            id=1,
            name="Coca Cola 600ml",
            price=2.50,
            category="Beverages",
            stock=100
        ),
        Product(
            id=2,
            name="Bread",
            price=1.20,
            category="Bakery",
            stock=50
        )
    ]
    return products

@app.post("/sales", response_model=Sale)
async def create_sale(sale: Sale):
    """
    Create a new sale with the specified items.
    
    Args:
        sale: Sale object containing items and other sale details
    
    Returns:
        Created sale object
    """
    try:
        # TODO: Implement database logic
        # For now, just return the received sale
        return sale
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales", response_model=List[Sale])
async def get_sales():
    """
    Get list of all sales.
    """
    # TODO: Implement database logic
    # For now, return example data
    sales = [
        Sale(
            items=[
                SaleItem(product_id=1, quantity=2, unit_price=2.50),
                SaleItem(product_id=2, quantity=1, unit_price=1.20)
            ],
            total=6.20,
            date=datetime.now(),
            notes="Example sale"
        )
    ]
    return sales

@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Voice POS API",
        "version": "1.0.0",
        "description": "Voice-controlled Point of Sale system API"
    } 