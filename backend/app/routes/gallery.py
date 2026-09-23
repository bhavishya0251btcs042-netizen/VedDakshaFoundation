import os
import time
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from datetime import datetime
from bson import ObjectId
from typing import Optional
from app.database import get_collection
from app.models import GalleryCreate
from app.utils import serialize_doc, serialize_docs
from app.middleware import get_current_admin

router = APIRouter(prefix="/gallery", tags=["gallery"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "gallery")
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError:
    pass

@router.get("")
def get_gallery(category: Optional[str] = None):
    gallery_col = get_collection("gallery")
    try:
        filter_query = {}
        if category:
            filter_query["category"] = category
        cursor = gallery_col.find(filter_query).sort([("order", 1), ("createdAt", -1)])
        images = list(cursor)
        return serialize_docs(images)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_gallery(
    occasion: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    category: Optional[str] = Form("general"),
    order: Optional[int] = Form(0),
    eventRef: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    gallery_col = get_collection("gallery")
    try:
        # Determine caption: occasion takes priority, then caption param, then url-derived
        final_caption = occasion or caption or ""

        # Determine image URL: uploaded file takes priority over url field
        image_url = url or ""
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"gallery_{int(time.time() * 1000)}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            content = await image.read()
            with open(filepath, "wb") as f:
                f.write(content)
            image_url = f"/gallery-images/{filename}"

        gallery_doc = {
            "url": image_url,
            "caption": final_caption,
            "occasion": final_caption,
            "category": category or "general",
            "order": int(order or 0),
            "createdAt": datetime.utcnow()
        }
        if eventRef:
            if ObjectId.is_valid(eventRef):
                gallery_doc["eventRef"] = ObjectId(eventRef)
            else:
                gallery_doc["eventRef"] = eventRef

        result = gallery_col.insert_one(gallery_doc)
        gallery_doc["_id"] = result.inserted_id
        return serialize_doc(gallery_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{image_id}")
async def update_gallery(
    image_id: str,
    occasion: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    order: Optional[int] = Form(None),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    gallery_col = get_collection("gallery")
    try:
        if not ObjectId.is_valid(image_id):
            raise HTTPException(status_code=400, detail="Invalid image ID")
        existing = gallery_col.find_one({"_id": ObjectId(image_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Not found")

        updates = {}
        final_caption = occasion or caption
        if final_caption is not None:
            updates["caption"] = final_caption
            updates["occasion"] = final_caption
        if category is not None:
            updates["category"] = category
        if order is not None:
            updates["order"] = int(order)
        if url is not None:
            updates["url"] = url

        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"gallery_{int(time.time() * 1000)}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            content = await image.read()
            with open(filepath, "wb") as f:
                f.write(content)
            updates["url"] = f"/gallery-images/{filename}"

        if updates:
            gallery_col.update_one({"_id": ObjectId(image_id)}, {"$set": updates})

        updated = gallery_col.find_one({"_id": ObjectId(image_id)})
        return serialize_doc(updated)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{image_id}")
def delete_gallery(image_id: str, admin_payload: dict = Depends(get_current_admin)):
    gallery_col = get_collection("gallery")
    try:
        if not ObjectId.is_valid(image_id):
            raise HTTPException(status_code=400, detail="Invalid image ID")
        result = gallery_col.delete_one({"_id": ObjectId(image_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return {"message": "Deleted"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

