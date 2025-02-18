from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .migrations import run_migrations

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./pos.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Create sessionmaker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    """Dependency to get a database session."""
    async with async_session() as session:
        yield session

# Function to initialize the database
async def init_db():
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Run migrations after creating tables
    try:
        run_migrations()
        print("Database initialized and migrations completed")
    except Exception as e:
        print(f"Error during database initialization: {str(e)}") 