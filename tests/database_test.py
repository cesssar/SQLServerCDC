import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.database import Database


def test_database_connection():
    db = Database(
        server=settings.DB_SERVER,
        database=settings.DB_DATABASE,
        username=settings.DB_USERNAME,
        password=settings.DB_PASSWORD
    )
    try:
        db.connect()
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:        
        db.disconnect()

if __name__ == "__main__":
    test_database_connection()