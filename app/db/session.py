from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

def get_database_url():
    """Get the appropriate database URL for the environment"""
    database_url = settings.DATABASE_URL
    
    # Handle SQLite for development
    if database_url.startswith('sqlite:///'):
        return database_url.replace('sqlite:///', 'sqlite+aiosqlite:///')
    
    # Handle PostgreSQL for production
    if database_url.startswith('postgresql://'):
        return database_url.replace('postgresql://', 'postgresql+asyncpg://')
    
    return database_url

# Create async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.DEBUG,
)

# Create async session factory
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close() 