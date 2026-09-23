from pymongo import MongoClient
from fastapi import HTTPException
from app.config import Config

client = None
db = None

ATLAS_URI = "mongodb+srv://kumarbhavishaya0_db_user:Y8E49VCMEMLf4VYg@cluster0.zl7pf18.mongodb.net/?appName=Cluster0"

def init_db():
    global client, db
    uri = Config.MONGODB_URI
    if not uri or "<username>" in uri or "xxxxx" in uri or "localhost" in uri:
        uri = ATLAS_URI
        
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        try:
            db = client.get_default_database()
            if db is None:
                db = client.get_database("veddaksha")
        except Exception:
            db = client.get_database("veddaksha")
    except Exception as e:
        print(f"[WARNING] Could not initialize MongoDB client: {e}")
        try:
            client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=5000)
            db = client.get_database("veddaksha")
        except Exception as e2:
            print(f"[ERROR] Atlas connection fallback failed: {e2}")
            client = None
            db = None

init_db()

def get_collection(name: str):
    if db is None:
        init_db()
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection is not configured or is unavailable. Please check MONGODB_URI in backend/.env"
        )
    return db[name]

def check_db_connection():
    if client is None or db is None:
        init_db()
    if client is None or db is None:
        return False
    try:
        client.admin.command('ismaster')
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        init_db()
        try:
            client.admin.command('ismaster')
            return True
        except Exception:
            return False
