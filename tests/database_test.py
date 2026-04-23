import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Database

def test_database_connection():
    db = Database(server="192.168.1.206", database="DATABASE_TESTE", username="sa", password="YourSecurePassword123!")
    try:
        db.connect()
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:        
        db.disconnect()

if __name__ == "__main__":
    test_database_connection()