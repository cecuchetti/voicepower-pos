from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import tempfile
import os
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload, Session
from server.database.database import get_session, init_db
from server.database.models import Product as ProductModel, Sale as SaleModel, SaleItem as SaleItemModel, Cart as CartModel, CartItem as CartItemModel
from server.schemas import Product, ProductCreate, Sale, SaleCreate, CartItemCreate, CartItem, Cart
from server.audio_processor import AudioProcessor, AudioConfig, AudioProcessingError
from server.config import config
from server.services.llm.openai_service import OpenAIService
from datetime import datetime
from server.services.image_service import ImageService

app = FastAPI(title="Voice POS API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global audio processor instance
audio_processor = AudioProcessor()

@app.on_event("startup")
async def startup():
    await init_db()

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
            
            # Process the audio file
            processor = AudioProcessor()
            text = await processor.process_audio_file_to_text(temp_audio.name)
            
            print(f"Recognized text from file {audio_file.filename}: {text}")
            
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
async def get_products(session: AsyncSession = Depends(get_session)):
    """Return list of available products."""
    result = await session.execute(select(ProductModel))
    products = result.scalars().all()
    return products

@app.post("/products", response_model=Product)
async def create_product(
    product: ProductCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new product."""
    db_product = ProductModel(
        name=product.name,
        price=product.price,
        category=product.category,
        stock=product.stock,
        image=ImageService.get_random_product_image()  # Asignar imagen aleatoria
    )
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    return db_product

@app.post("/sales", response_model=Sale)
async def create_sale(
    sale: SaleCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new sale with items."""
    db_sale = SaleModel(total=sale.total, notes=sale.notes)
    session.add(db_sale)
    
    for item in sale.items:
        db_item = SaleItemModel(
            sale=db_sale,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        session.add(db_item)
    
    await session.commit()
    await session.refresh(db_sale)
    return db_sale

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

@app.post("/carts", response_model=Cart)
async def create_cart(session: AsyncSession = Depends(get_session)):
    """Create a new shopping cart."""
    db_cart = CartModel()
    session.add(db_cart)
    await session.commit()
    await session.refresh(db_cart)
    return db_cart

@app.post("/carts/{cart_id}/items", response_model=CartItem)
async def add_item_to_cart(
    cart_id: int,
    item: CartItemCreate,
    session: AsyncSession = Depends(get_session)
):
    """Add an item to the cart."""
    # Verificar que el carrito existe y está activo
    cart = await session.get(CartModel, cart_id)
    if not cart or cart.status != "active":
        raise HTTPException(status_code=404, detail="Active cart not found")
    
    # Crear el item del carrito
    db_item = CartItemModel(
        cart_id=cart_id,
        product_id=item.product_id,
        product_name=item.product_name,
        quantity=item.quantity,
        unit_price=item.unit_price
    )
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item

@app.get("/carts/{cart_id}", response_model=Cart)
async def get_cart(cart_id: int, session: AsyncSession = Depends(get_session)):
    """Get cart details with product information."""
    # Obtener el carrito con sus items usando selectinload
    query = select(CartModel).options(selectinload(CartModel.items)).where(CartModel.id == cart_id)
    result = await session.execute(query)
    cart = result.scalar_one_or_none()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return cart

@app.post("/carts/{cart_id}/checkout", response_model=None)
async def checkout_cart(cart_id: int, session: AsyncSession = Depends(get_session)):
    """
    Process checkout and clear all active carts
    """
    try:
        # Delete all cart items from active carts
        delete_items_query = delete(CartItemModel).where(
            CartItemModel.cart_id.in_(
                select(CartModel.id).where(CartModel.status == "active")
            )
        )
        await session.execute(delete_items_query)
        
        # Delete all active carts
        delete_carts_query = delete(CartModel).where(CartModel.status == "active")
        await session.execute(delete_carts_query)
        
        # Commit changes
        await session.commit()
        
        return {"message": "Checkout successful"}
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing checkout: {str(e)}"
        )

@app.delete("/carts/{cart_id}", response_model=None)
async def delete_cart(cart_id: int, session: AsyncSession = Depends(get_session)):
    """
    Delete a cart and all its items
    """
    # Get the cart using async query
    query = select(CartModel).where(CartModel.id == cart_id)
    result = await session.execute(query)
    cart = result.scalar_one_or_none()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    try:
        # Delete all cart items first
        delete_items_query = delete(CartItemModel).where(CartItemModel.cart_id == cart_id)
        await session.execute(delete_items_query)
        
        # Delete the cart
        delete_cart_query = delete(CartModel).where(CartModel.id == cart_id)
        await session.execute(delete_cart_query)
        
        # Commit changes
        await session.commit()
        
        return {"message": "Cart deleted successfully"}
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting cart: {str(e)}"
        )

@app.post("/audio/process/cart")
async def process_audio_to_cart(
    audio_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Process an audio file, convert to text, and create a shopping cart with the items.
    """
    temp_audio = None
    try:
        # Procesar el audio a texto
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_audio = temp_file.name
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.flush()
        
        # Procesar el audio de forma asíncrona
        text = await audio_processor.process_audio_file_to_text(temp_audio)
        print(f"Texto reconocido: {text}")
        
        # Convertir texto a lista de compras
        openai_service = OpenAIService()
        shopping_list = await openai_service.text_to_shopping_list(text + " con precios que debes inventar")
        print(f"Lista de compras procesada: {shopping_list}")
        
        if not shopping_list or not isinstance(shopping_list, list):
            raise HTTPException(
                status_code=400,
                detail="Invalid shopping list format"
            )

        # Crear un nuevo carrito
        cart = CartModel(status="active")
        session.add(cart)
        
        # Agregar items al carrito directamente desde la lista de OpenAI
        cart_items = []
        for item in shopping_list:
            try:
                # Asignar un precio por defecto de 100 si no viene precio
                default_price = 100.0  # Precio por defecto temporal
                cart_item = CartItemModel(
                    cart=cart,
                    product_name=str(item.get('name', 'Unknown Item')),
                    quantity=float(item.get('quantity', 1)),
                    unit_price=float(item.get('unit_price', default_price) or default_price)  # Usar precio por defecto si es None o 0
                )
                cart_items.append(cart_item)
                session.add(cart_item)
                print(f"Added item to cart: {cart_item.product_name}, quantity: {cart_item.quantity}, price: {cart_item.unit_price}")
            except (ValueError, TypeError) as e:
                print(f"Error processing item {item}: {str(e)}")
                continue
        
        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="No valid items could be added to cart"
            )
        
        # Commit the transaction
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error saving to database: {str(e)}"
            )
        
        # Refresh to get the updated data
        await session.refresh(cart)
        
        return {
            "text": text,
            "cart_id": cart.id,
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price
                } for item in cart.items
            ],
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error processing cart: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Limpiar el archivo temporal
        if temp_audio and os.path.exists(temp_audio):
            os.unlink(temp_audio)

@app.get("/carts", response_model=List[Cart])
async def list_carts(
    status: str = None,
    session: AsyncSession = Depends(get_session)
):
    """List all shopping carts, optionally filtered by status."""
    # Construir query con selectinload
    query = select(CartModel).options(selectinload(CartModel.items))
    if status:
        query = query.where(CartModel.status == status)
    
    result = await session.execute(query)
    carts = result.scalars().all()
    
    return carts 