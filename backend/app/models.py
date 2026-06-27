from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ── AUTH SCHEMAS ──
class AdminLogin(BaseModel):
    email: str
    password: str

class ChangePassword(BaseModel):
    oldPassword: str
    newPassword: str

# ── BLOG SCHEMAS ──
# Blog creation is multipart/form-data, but we can model JSON fields if needed.

# ── DONATION SCHEMAS ──
class DonationCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    amount: float
    purpose: Optional[str] = None
    method: Optional[str] = "upi"
    txnId: Optional[str] = None
    message: Optional[str] = None
    isAnonymous: Optional[bool] = False

class DonationStatusUpdate(BaseModel):
    status: str

# ── GALLERY SCHEMAS ──
class GalleryCreate(BaseModel):
    url: str
    caption: Optional[str] = ""
    category: Optional[str] = "general"
    eventRef: Optional[str] = None
    order: Optional[int] = 0

# ── CONTACT SCHEMAS ──
class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str
    type: Optional[str] = "general"

# ── RAZORPAY SCHEMAS ──
class RazorpayOrderCreate(BaseModel):
    amount: float
    purpose: Optional[str] = "General donation"
    name: Optional[str] = "Donor"
    email: Optional[str] = None
    phone: Optional[str] = None

class RazorpayPaymentVerify(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    amount: float
    purpose: Optional[str] = None

# ── VOLUNTEER SCHEMAS ──
class VolunteerField(BaseModel):
    id: str
    label: str
    labelHindi: str
    type: str
    required: bool = False
    enabled: bool = True
    options: Optional[List[str]] = None

class VolunteerConfigUpdate(BaseModel):
    fields: List[VolunteerField]

class VolunteerEmailSend(BaseModel):
    subject: str
    body: str

# ── CONNECTION SCHEMAS ──
class ConnectionCreate(BaseModel):
    name: str
    role: str
    bio: Optional[str] = ""
    imageUrl: Optional[str] = ""
    order: Optional[int] = 0

