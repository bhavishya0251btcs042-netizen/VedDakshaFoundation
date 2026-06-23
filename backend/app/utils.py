import bcrypt
import jwt
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import Config
from bson import ObjectId

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def create_jwt_token(data: dict, expires_in_days: int = 7) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=expires_in_days)
    payload.update({"exp": expire})
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

def send_confirmation_email(to_email: str, name: str, amount: float, donation_id: str):
    if not to_email or Config.EMAIL_PASS == 'your_gmail_app_password_here' or not Config.EMAIL_USER or not Config.EMAIL_PASS:
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🙏 Thank you for your donation — Ved Daksha Foundation"
        msg["From"] = f'"Ved Daksha Foundation" <{Config.EMAIL_USER}>'
        msg["To"] = to_email
        
        html = f"""<div style="font-family:sans-serif;max-width:500px">
          <h2 style="color:#1B6B3A">Thank you, {name}!</h2>
          <p>We have received your donation of <strong>₹{amount}</strong>. Your support directly reaches our children.</p>
          <p><strong>Reference ID:</strong> {donation_id}</p>
          <p>Our team will verify your payment and send an acknowledgement within 24 hours.</p>
          <p>For any queries: <a href="tel:{Config.DONATION_PHONE}">{Config.DONATION_PHONE}</a></p>
          <p style="color:#888;font-size:12px">Ved Daksha Foundation · 7/56, Chiranjeev Vihar, Ghaziabad</p>
        </div>"""
        
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
            server.sendmail(Config.EMAIL_USER, to_email, msg.as_string())
        print(f"Confirmation email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_custom_email(to_email: str, subject: str, body_html: str, attachments: list = None):
    if not to_email or Config.EMAIL_PASS == 'your_gmail_app_password_here' or not Config.EMAIL_USER or not Config.EMAIL_PASS:
        raise ValueError("SMTP email credentials are not fully configured in backend/.env")
    try:
        import mimetypes
        from email.mime.base import MIMEBase
        from email import encoders

        if attachments:
            msg = MIMEMultipart("mixed")
            msg["Subject"] = subject
            msg["From"] = f'"Ved Daksha Foundation" <{Config.EMAIL_USER}>'
            msg["To"] = to_email
            
            # Alternative wrapper for body content
            msg_alt = MIMEMultipart("alternative")
            msg_alt.attach(MIMEText(body_html, "html"))
            msg.attach(msg_alt)
            
            # Attach files
            for filename, content in attachments:
                ctype, encoding = mimetypes.guess_type(filename)
                if ctype is None or encoding:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                
                part = MIMEBase(maintype, subtype)
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(part)
        else:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f'"Ved Daksha Foundation" <{Config.EMAIL_USER}>'
            msg["To"] = to_email
            msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
            server.sendmail(Config.EMAIL_USER, to_email, msg.as_string())
        print(f"Custom email sent to {to_email}")
    except Exception as e:
        print(f"Error sending custom email: {e}")
        raise e

def serialize_doc(doc):
    if doc is None:
        return None
    d = dict(doc)
    for k, v in d.items():
        if isinstance(v, ObjectId):
            d[k] = str(v)
        elif isinstance(v, datetime):
            d[k] = v.isoformat()
        elif isinstance(v, list):
            d[k] = [serialize_doc(x) if isinstance(x, dict) else (str(x) if isinstance(x, ObjectId) else x) for x in v]
        elif isinstance(v, dict):
            d[k] = serialize_doc(v)
    return d

def serialize_docs(docs):
    return [serialize_doc(doc) for doc in docs]
