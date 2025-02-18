import asyncio
from server.database.database import async_session
from server.database.models import Product
from server.services.image_service import ImageService

async def seed_products():
    async with async_session() as session:
        products = [
            Product(
                name="Coca Cola 600ml",
                price=2.50,
                category="Beverages",
                stock=100,
                image=ImageService.get_random_product_image()
            ),
            Product(
                name="Pan",
                price=1.20,
                category="Bakery",
                stock=50,
                image=ImageService.get_random_product_image()
            ),
            # Add more products here
        ]
        
        for product in products:
            session.add(product)
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_products()) 