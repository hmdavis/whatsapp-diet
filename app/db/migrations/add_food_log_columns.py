from sqlalchemy import create_engine, text
from app.core.config import get_settings

settings = get_settings()

def upgrade():
    """Add new columns to food_logs table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Add new columns
        conn.execute(text("""
            ALTER TABLE food_logs 
            ADD COLUMN normalized_title VARCHAR;
        """))
        

if __name__ == "__main__":
    print("Adding new columns to food_logs table...")
    upgrade()
    print("Migration completed successfully!") 