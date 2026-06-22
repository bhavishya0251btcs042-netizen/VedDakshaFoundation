from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from typing import Optional
from app.database import get_collection
from app.models import GalleryCreate
from app.utils import serialize_doc, serialize_docs
from app.middleware import get_current_admin

router = APIRouter(prefix="/gallery", tags=["gallery"])

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
def create_gallery(data: GalleryCreate, admin_payload: dict = Depends(get_current_admin)):
    gallery_col = get_collection("gallery")
    try:
        gallery_doc = {
            "url": data.url,
            "caption": data.caption,
            "category": data.category,
            "order": data.order or 0,
            "createdAt": datetime.utcnow()
        }
        if data.eventRef:
            if ObjectId.is_valid(data.eventRef):
                gallery_doc["eventRef"] = ObjectId(data.eventRef)
            else:
                gallery_doc["eventRef"] = data.eventRef
                
        result = gallery_col.insert_one(gallery_doc)
        gallery_doc["_id"] = result.inserted_id
        return serialize_doc(gallery_doc)
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
