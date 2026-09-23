import os
import time
import base64
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_collection
from app.utils import serialize_doc, serialize_docs
from app.middleware import get_current_admin

router = APIRouter(prefix="/connections", tags=["connections"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "connections")
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError:
    pass

@router.get("")
def get_connections():
    col = get_collection("connections")
    try:
        docs = list(col.find({}).sort("order", 1))
        return serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_connection(
    name: str = Form(...),
    role: str = Form(...),
    bio: Optional[str] = Form(""),
    order: Optional[int] = Form(0),
    image: Optional[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    col = get_collection("connections")
    try:
        image_url = ""
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"conn_{int(time.time() * 1000)}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            content = await image.read()
            with open(filepath, "wb") as f:
                f.write(content)
            image_url = f"/connection-images/{filename}"

        doc = {
            "name": name,
            "role": role,
            "bio": bio or "",
            "imageUrl": image_url,
            "order": int(order or 0),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        result = col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return serialize_doc(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{conn_id}")
async def update_connection(
    conn_id: str,
    name: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    order: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    col = get_collection("connections")
    try:
        if not ObjectId.is_valid(conn_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        existing = col.find_one({"_id": ObjectId(conn_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Not found")

        updates = {"updatedAt": datetime.utcnow()}
        if name is not None: updates["name"] = name
        if role is not None: updates["role"] = role
        if bio is not None: updates["bio"] = bio
        if order is not None: updates["order"] = int(order)

        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"conn_{int(time.time() * 1000)}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            content = await image.read()
            with open(filepath, "wb") as f:
                f.write(content)
            updates["imageUrl"] = f"/connection-images/{filename}"

        col.update_one({"_id": ObjectId(conn_id)}, {"$set": updates})
        updated = col.find_one({"_id": ObjectId(conn_id)})
        return serialize_doc(updated)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{conn_id}")
def delete_connection(conn_id: str, admin_payload: dict = Depends(get_current_admin)):
    col = get_collection("connections")
    try:
        if not ObjectId.is_valid(conn_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        result = col.delete_one({"_id": ObjectId(conn_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return {"message": "Deleted"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
