from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from app.database import get_collection
from app.models import ContactCreate
from app.utils import serialize_doc, serialize_docs
from app.middleware import get_current_admin

router = APIRouter(prefix="/contact", tags=["contact"])

@router.post("")
def create_contact(data: ContactCreate):
    contacts_col = get_collection("contacts")
    try:
        contact_doc = {
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "subject": data.subject,
            "message": data.message,
            "type": data.type,
            "isRead": False,
            "createdAt": datetime.utcnow()
        }
        contacts_col.insert_one(contact_doc)
        return {"message": "Message received! We will contact you soon."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_contacts(admin_payload: dict = Depends(get_current_admin)):
    contacts_col = get_collection("contacts")
    try:
        cursor = contacts_col.find({}).sort("createdAt", -1).limit(50)
        messages = list(cursor)
        unread = contacts_col.count_documents({"isRead": False})
        return {
            "messages": serialize_docs(messages),
            "unread": unread
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{contact_id}/read")
def mark_contact_read(contact_id: str, admin_payload: dict = Depends(get_current_admin)):
    contacts_col = get_collection("contacts")
    try:
        if not ObjectId.is_valid(contact_id):
            raise HTTPException(status_code=400, detail="Invalid contact ID")
        result = contacts_col.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": {"isRead": True}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"message": "Marked as read"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
