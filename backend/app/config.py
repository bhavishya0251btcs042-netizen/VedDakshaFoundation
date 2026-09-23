import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly find backend/.env file regardless of current working directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

class Config:
    MONGODB_URI = os.getenv(
        "MONGODB_URI", 
        "mongodb+srv://kumarbhavishaya0_db_user:Y8E49VCMEMLf4VYg@cluster0.zl7pf18.mongodb.net/?appName=Cluster0"
    )
    JWT_SECRET = os.getenv("JWT_SECRET", "ved_daksha_foundation_secret_jwt_token_key_2026_secure_sha256")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@veddakshafoundation.org")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "VedDaksha@Admin2024")
    PORT = int(os.getenv("PORT", 5000))
    EMAIL_USER = os.getenv("EMAIL_USER", "bhaviengineer720@gmail.com")
    EMAIL_PASS = os.getenv("EMAIL_PASS", "fvknbaxnpqruyatp")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_T4aJralPhxr88y")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "rx1hISOkyAKOM73GXVKDgy3Y")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://veddakshafoundation-production.up.railway.app")
    
    # Donation configurations
    DONATION_UPI_ID = os.getenv("DONATION_UPI_ID", "veddaksha@idfcbank")
    DONATION_PHONE = os.getenv("DONATION_PHONE", "9068188593")
    DONATION_EMAIL = os.getenv("DONATION_EMAIL", "kumarbhavishya384@gmail.com")
    DONATION_SECOND_PHONE = os.getenv("DONATION_SECOND_PHONE", "7351878392")
