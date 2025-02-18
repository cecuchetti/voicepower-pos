from sqlalchemy import create_engine, text, inspect

# Usar la misma URL que en database.py
DATABASE_URL = "sqlite:///./pos.db"  # Note que aquí no usamos aiosqlite

def column_exists(inspector, table_name, column_name):
    """Check if a column exists in a table"""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def run_migrations():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        try:
            # Check if product_name column already exists
            if not column_exists(inspector, 'cart_items', 'product_name'):
                # Add product_name column to cart_items
                conn.execute(text("""
                    ALTER TABLE cart_items 
                    ADD COLUMN product_name TEXT NOT NULL DEFAULT 'Unknown Product';
                """))
                print("Added product_name column")
            else:
                print("product_name column already exists")
            
            # Recreate table with updated structure
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cart_items_new (
                    id INTEGER PRIMARY KEY,
                    cart_id INTEGER REFERENCES carts(id),
                    product_id INTEGER,
                    product_name TEXT NOT NULL,
                    quantity FLOAT,
                    unit_price FLOAT
                );
            """))
            
            # Copy existing data only if old table exists
            if 'cart_items' in inspector.get_table_names():
                conn.execute(text("""
                    INSERT OR IGNORE INTO cart_items_new (id, cart_id, product_id, product_name, quantity, unit_price)
                    SELECT id, cart_id, product_id, 
                           COALESCE(product_name, 'Unknown Product') as product_name, 
                           quantity, unit_price
                    FROM cart_items;
                """))
                
                # Drop old table and rename new one
                conn.execute(text("DROP TABLE cart_items;"))
                conn.execute(text("ALTER TABLE cart_items_new RENAME TO cart_items;"))
            
            # Add image column to products if it doesn't exist
            if not column_exists(inspector, 'products', 'image'):
                conn.execute(text("""
                    ALTER TABLE products
                    ADD COLUMN image TEXT;
                """))
                
                # Update existing products with random images
                for i in range(1, 16):  # 15 images
                    conn.execute(text(f"""
                        UPDATE products 
                        SET image = '/images/products/{i}.png'
                        WHERE id % 15 = {i-1};
                    """))
            
            conn.commit()
            print("Migrations completed successfully")
            
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migrations() 