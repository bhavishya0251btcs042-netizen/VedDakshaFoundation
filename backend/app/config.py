import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

class Config:
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/veddaksha")
    JWT_SECRET = os.getenv("JWT_SECRET", "change_this_to_a_very_long_random_secret_string_123456")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@veddakshafoundation.org")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "VedDaksha@Admin2024")
    PORT = int(os.getenv("PORT", 5000))
    EMAIL_USER = os.getenv("EMAIL_USER", "veddakshafoundation22@gmail.com")
    EMAIL_PASS = os.getenv("EMAIL_PASS", "your_gmail_app_password_here")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_live_xxxxxxxxxx")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "your_razorpay_secret")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://veddakshafoundation.org")
    
    # Donation configurations
    DONATION_UPI_ID = os.getenv("DONATION_UPI_ID", "veddakshafoundation22@gmail.com")
    DONATION_PHONE = os.getenv("DONATION_PHONE", "8700785399")
    DONATION_EMAIL = os.getenv("DONATION_EMAIL", "veddakshafoundation22@gmail.com")
    DONATION_SECOND_PHONE = os.getenv("DONATION_SECOND_PHONE", "8595656658")
