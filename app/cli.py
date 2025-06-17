import asyncio
import json
from httpx import AsyncClient
from app.main import app
from app.db.session import async_session
from app.models.user import User
from sqlalchemy import select

async def create_test_user():
    """Create a test user if none exists"""
    async with async_session() as session:
        stmt = select(User).where(User.phone_number == "+12014103350")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                phone_number="+12014103350",
                target_calories=2853,
                target_protein=209,
                target_carbs=367,
                target_fats=57,
                height=185, # cm
                weight=86.2, # kg
                age=33, # years
                activity_level="active",
                dietary_restrictions="none"
            )
            session.add(user)
            await session.commit()
            print("Created test user with phone number: +12014103350")
        return user

async def send_message(message: str):
    """Send a message to the bot and get the response"""
    # Create test user if needed
    await create_test_user()
    
    # Prepare the message payload
    payload = {
        "message": message,
        "from": "+12014103350"  # Test phone number
    }
    
    # Use httpx AsyncClient to make the request
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/webhook/message", json=payload)
        
        if response.status_code == 200:
            print("\nBot's response:")
            print(response.json()["response"])
        else:
            print(f"\nError: {response.status_code}")
            print(response.json())

async def main_async():
    print("Welcome to the Diet Bot CLI!")
    print("Type 'exit' to quit")
    print("Example messages:")
    print("- 'I had a chicken salad for lunch'")
    print("- 'How am I doing on my protein goals?'")
    print("- 'What should I eat to meet my macros?'")
    print("\nEnter your message:")
    
    while True:
        message = input("> ").strip()
        if message.lower() == 'exit':
            break
        
        if message:
            await send_message(message)
        print("\nEnter another message (or 'exit' to quit):")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 