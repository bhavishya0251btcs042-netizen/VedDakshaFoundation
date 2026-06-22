import os
import time
import json
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_collection
from app.utils import serialize_doc, serialize_docs
from app.middleware import get_current_admin

router = APIRouter(prefix="/events", tags=["events"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "events")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
def get_events(upcoming: Optional[str] = None, limit: int = 20):
    events_col = get_collection("events")
    try:
        filter_query = {"isPublished": True}
        if upcoming == "true":
            filter_query["isUpcoming"] = True
            sort_dir = 1
        elif upcoming == "false":
            filter_query["isUpcoming"] = False
            sort_dir = -1
        else:
            sort_dir = -1  # default sort
            
        cursor = events_col.find(filter_query).sort("date", sort_dir).limit(limit)
        events = list(cursor)
        return serialize_docs(events)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{event_id}")
def get_event(event_id: str):
    events_col = get_collection("events")
    try:
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID")
        event = events_col.find_one({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Not found")
        return serialize_doc(event)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_event(
    title: str = Form(...),
    titleHindi: Optional[str] = Form(None),
    description: str = Form(...),
    descriptionHindi: Optional[str] = Form(None),
    date: str = Form(...),
    time_str: Optional[str] = Form(None, alias="time"),
    location: Optional[str] = Form("7/56, Chiranjeev Vihar, Ghaziabad"),
    category: Optional[str] = Form("other"),
    attendees: Optional[int] = Form(0),
    highlights: Optional[str] = Form(None),
    isUpcoming: Optional[str] = Form("true"),
    images: List[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    events_col = get_collection("events")
    try:
        uploaded_images = []
        if images:
            for file in images:
                if file.filename:
                    ext = os.path.splitext(file.filename)[1]
                    filename = f"event_{int(time.time() * 1000)}_{len(uploaded_images)}{ext}"
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    content = await file.read()
                    with open(filepath, "wb") as f:
                        f.write(content)
                    uploaded_images.append(f"/event-images/{filename}")
                    
        parsed_highlights = []
        if highlights:
            try:
                parsed_highlights = json.loads(highlights)
            except Exception:
                pass
                
        try:
            event_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
        except Exception:
            event_date = datetime.utcnow()
            
        event_doc = {
            "title": title,
            "titleHindi": titleHindi,
            "description": description,
            "descriptionHindi": descriptionHindi,
            "date": event_date,
            "time": time_str,
            "location": location,
            "category": category,
            "images": uploaded_images,
            "coverImage": uploaded_images[0] if uploaded_images else "",
            "isUpcoming": isUpcoming.lower() != "false",
            "isPublished": True,
            "attendees": int(attendees or 0),
            "highlights": parsed_highlights,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = events_col.insert_one(event_doc)
        event_doc["_id"] = result.inserted_id
        return serialize_doc(event_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{event_id}")
async def update_event(
    event_id: str,
    title: Optional[str] = Form(None),
    titleHindi: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    descriptionHindi: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    time_str: Optional[str] = Form(None, alias="time"),
    location: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    attendees: Optional[int] = Form(None),
    highlights: Optional[str] = Form(None),
    isUpcoming: Optional[str] = Form(None),
    images: List[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    events_col = get_collection("events")
    try:
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID")
            
        existing = events_col.find_one({"_id": ObjectId(event_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Not found")
            
        updates = {"updatedAt": datetime.utcnow()}
        if title is not None: updates["title"] = title
        if titleHindi is not None: updates["titleHindi"] = titleHindi
        if description is not None: updates["description"] = description
        if descriptionHindi is not None: updates["descriptionHindi"] = descriptionHindi
        if time_str is not None: updates["time"] = time_str
        if location is not None: updates["location"] = location
        if category is not None: updates["category"] = category
        if attendees is not None: updates["attendees"] = int(attendees)
        if isUpcoming is not None: updates["isUpcoming"] = isUpcoming.lower() != "false"
        
        if date is not None:
            try:
                updates["date"] = datetime.fromisoformat(date.replace("Z", "+00:00"))
            except Exception:
                pass
                
        if highlights is not None:
            try:
                updates["highlights"] = json.loads(highlights)
            except Exception:
                pass
                
        new_imgs = []
        if images:
            for file in images:
                if file.filename:
                    ext = os.path.splitext(file.filename)[1]
                    filename = f"event_{int(time.time() * 1000)}_{len(new_imgs)}{ext}"
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    content = await file.read()
                    with open(filepath, "wb") as f:
                        f.write(content)
                    new_imgs.append(f"/event-images/{filename}")
                    
        if new_imgs:
            events_col.update_one(
                {"_id": ObjectId(event_id)},
                {
                    "$set": updates,
                    "$push": {"images": {"$each": new_imgs}}
                }
            )
            if not existing.get("coverImage") and not updates.get("coverImage"):
                events_col.update_one(
                    {"_id": ObjectId(event_id)},
                    {"$set": {"coverImage": new_imgs[0]}}
                )
        else:
            events_col.update_one({"_id": ObjectId(event_id)}, {"$set": updates})
            
        updated = events_col.find_one({"_id": ObjectId(event_id)})
        return serialize_doc(updated)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{event_id}")
def delete_event(event_id: str, admin_payload: dict = Depends(get_current_admin)):
    events_col = get_collection("events")
    try:
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID")
        result = events_col.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return {"message": "Deleted"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
