from pymongo import MongoClient
from fastapi import HTTPException
from app.config import Config

client = None
db = None

# Initialize MongoDB Client lazily and catch configuration/connection issues
try:
    # Check if MONGODB_URI is still the placeholder template
    if Config.MONGODB_URI and "<username>" not in Config.MONGODB_URI and "xxxxx" not in Config.MONGODB_URI:
        client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=2000)
        try:
            db = client.get_default_database()
            if db is None:
                db = client.get_database("veddaksha")
        except Exception:
            db = client.get_database("veddaksha")
    else:
        print("[WARNING] MONGODB_URI is unconfigured or using placeholder template.")
except Exception as e:
    print(f"[WARNING] Could not initialize MongoDB client: {e}")
    client = None
    db = None

def get_collection(name: str):
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection is not configured or is unavailable. Please check MONGODB_URI in backend/.env"
        )
    return db[name]

def check_db_connection():
    if client is None or db is None:
        return False
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False
