from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from app.database import get_collection
from app.config import Config
from app.models import AdminLogin, ChangePassword
from app.utils import hash_password, verify_password, create_jwt_token, serialize_doc
from app.middleware import get_current_admin

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/setup")
def setup_admin():
    admins_col = get_collection("admins")
    try:
        count = admins_col.count_documents({})
        if count > 0:
            raise HTTPException(status_code=400, detail="Admin already exists")
            
        hashed = hash_password(Config.ADMIN_PASSWORD)
        admin = {
            "email": Config.ADMIN_EMAIL,
            "password": hashed,
            "name": "Dr. Usha Tyagi",
            "createdAt": datetime.utcnow()
        }
        admins_col.insert_one(admin)
        return {"message": "Admin created. Login now."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(data: AdminLogin):
    admins_col = get_collection("admins")
    try:
        admin = admins_col.find_one({"email": data.email})
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        if not verify_password(data.password, admin["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        token = create_jwt_token({"id": str(admin["_id"]), "email": admin["email"]})
        return {
            "token": token,
            "admin": {
                "name": admin.get("name", "Admin"),
                "email": admin["email"]
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/change-password")
def change_password(data: ChangePassword, admin_payload: dict = Depends(get_current_admin)):
    admins_col = get_collection("admins")
    try:
        admin_id = admin_payload.get("id")
        admin = admins_col.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
            
        if not verify_password(data.oldPassword, admin["password"]):
            raise HTTPException(status_code=400, detail="Old password incorrect")
            
        new_hashed = hash_password(data.newPassword)
        admins_col.update_one({"_id": ObjectId(admin_id)}, {"$set": {"password": new_hashed}})
        return {"message": "Password changed"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
