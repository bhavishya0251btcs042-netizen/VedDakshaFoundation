from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from app.database import get_collection
from app.config import Config
from app.models import DonationCreate, DonationStatusUpdate
from app.utils import serialize_doc, serialize_docs, send_confirmation_email
from app.middleware import get_current_admin

router = APIRouter(prefix="/donations", tags=["donations"])

@router.get("/config")
def get_donation_config():
    return {
        "upi_id": Config.DONATION_UPI_ID,
        "phone": Config.DONATION_PHONE,
        "email": Config.DONATION_EMAIL,
        "second_phone": Config.DONATION_SECOND_PHONE,
        "razorpay_key_id": Config.RAZORPAY_KEY_ID
    }

@router.post("")
def create_donation(data: DonationCreate):
    donations_col = get_collection("donations")
    try:
        donation_doc = {
            "name": data.name,
            "phone": data.phone,
            "email": data.email,
            "amount": data.amount,
            "purpose": data.purpose,
            "method": data.method,
            "txnId": data.txnId,
            "status": "pending",
            "message": data.message,
            "isAnonymous": data.isAnonymous,
            "createdAt": datetime.utcnow()
        }
        
        result = donations_col.insert_one(donation_doc)
        donation_id = str(result.inserted_id)
        
        if data.email:
            send_confirmation_email(data.email, data.name, data.amount, donation_id)
            
        return {"message": "Donation recorded", "id": donation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_donations(admin_payload: dict = Depends(get_current_admin)):
    donations_col = get_collection("donations")
    try:
        cursor = donations_col.find({}).sort("createdAt", -1).limit(100)
        donations = list(cursor)
        
        pipeline = [
            {"$match": {"status": "confirmed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        agg_result = list(donations_col.aggregate(pipeline))
        total_confirmed = agg_result[0]["total"] if agg_result else 0
        
        return {
            "donations": serialize_docs(donations),
            "totalConfirmed": total_confirmed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{donation_id}")
def update_donation_status(
    donation_id: str,
    data: DonationStatusUpdate,
    admin_payload: dict = Depends(get_current_admin)
):
    donations_col = get_collection("donations")
    try:
        if not ObjectId.is_valid(donation_id):
            raise HTTPException(status_code=400, detail="Invalid donation ID")
            
        result = donations_col.update_one(
            {"_id": ObjectId(donation_id)},
            {"$set": {"status": data.status}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Donation not found")
            
        updated = donations_col.find_one({"_id": ObjectId(donation_id)})
        return serialize_doc(updated)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
