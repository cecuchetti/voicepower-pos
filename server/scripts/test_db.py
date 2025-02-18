import asyncio
from sqlalchemy import text, select
from server.database.database import async_session, init_db
from server.database.models import Product, Sale, SaleItem, Base
from server.database.database import engine

async def test_database():
    # Clean and reinitialize the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop all tables
        await conn.run_sync(Base.metadata.create_all)  # Create tables again
    
    async with async_session() as session:
        # Create some products
        products = [
            Product(
                name="Coca Cola 600ml",
                price=2.50,
                category="Beverages",
                stock=100
            ),
            Product(
                name="Pan",
                price=1.20,
                category="Bakery",
                stock=50
            ),
            Product(
                name="Café",
                price=1.80,
                category="Beverages",
                stock=75
            )
        ]
        
        print("Creating products...")
        for product in products:
            session.add(product)
        await session.commit()
        
        # Read products (using ORM)
        print("\nReading products (using ORM):")
        result = await session.execute(select(Product))
        products = result.scalars().all()
        for product in products:
            print(f"Product: {product.name}, Price: {product.price}, Stock: {product.stock}")
        
        # Read products (using direct SQL)
        print("\nReading products (using SQL):")
        result = await session.execute(
            text("SELECT * FROM products")
        )
        for row in result:
            print(f"Product: {row}")
        
        # Create a sale
        print("\nCreating sale...")
        sale = Sale(total=5.20, notes="Test sale")
        session.add(sale)
        await session.commit()
        
        # Add items to the sale
        sale_items = [
            SaleItem(
                sale_id=sale.id,
                product_id=1,
                quantity=2,
                unit_price=2.50
            ),
            SaleItem(
                sale_id=sale.id,
                product_id=2,
                quantity=1,
                unit_price=1.20
            )
        ]
        
        for item in sale_items:
            session.add(item)
        await session.commit()
        
        # Read sales (using direct SQL)
        print("\nReading sales:")
        result = await session.execute(
            text("""
                SELECT s.id, s.total, s.notes, si.quantity, si.unit_price, p.name 
                FROM sales s 
                JOIN sale_items si ON s.id = si.sale_id 
                JOIN products p ON si.product_id = p.id
            """)
        )
        for row in result:
            print(f"Sale: {row}")

if __name__ == "__main__":
    asyncio.run(test_database()) 