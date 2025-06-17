from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.food_log import FoodLog

async def init_db():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    print("Creating database tables...")
    asyncio.run(init_db())
    print("Database tables created successfully!") 