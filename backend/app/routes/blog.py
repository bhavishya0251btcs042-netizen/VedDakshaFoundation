import os
import time
import json
import re
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from app.database import get_collection
from app.utils import serialize_doc, serialize_docs
from app.middleware import get_current_admin

router = APIRouter(prefix="/blog", tags=["blog"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "blog")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
def get_blogs():
    blogs_col = get_collection("blogs")
    try:
        cursor = blogs_col.find({"isPublished": True}).sort("createdAt", -1).limit(20)
        blogs = list(cursor)
        return serialize_docs(blogs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}")
def get_blog(slug: str):
    blogs_col = get_collection("blogs")
    try:
        blog = blogs_col.find_one_and_update(
            {"slug": slug, "isPublished": True},
            {"$inc": {"views": 1}},
            return_document=ReturnDocument.AFTER
        )
        if not blog:
            raise HTTPException(status_code=404, detail="Not found")
        return serialize_doc(blog)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_blog(
    title: str = Form(...),
    titleHindi: Optional[str] = Form(None),
    content: str = Form(...),
    contentHindi: Optional[str] = Form(None),
    excerpt: Optional[str] = Form(None),
    excerptHindi: Optional[str] = Form(None),
    category: Optional[str] = Form("general"),
    tags: Optional[str] = Form(None),
    author: Optional[str] = Form("Ved Daksha Foundation"),
    coverImage: Optional[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    blogs_col = get_collection("blogs")
    try:
        clean_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        slug = f"{clean_title}-{int(time.time() * 1000)}"
        
        cover_image_url = ""
        if coverImage and coverImage.filename:
            ext = os.path.splitext(coverImage.filename)[1]
            filename = f"blog_{int(time.time() * 1000)}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            content_bytes = await coverImage.read()
            with open(filepath, "wb") as f:
                f.write(content_bytes)
            cover_image_url = f"/blog-images/{filename}"
            
        parsed_tags = []
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except Exception:
                pass
                
        blog_doc = {
            "title": title,
            "titleHindi": titleHindi,
            "slug": slug,
            "content": content,
            "contentHindi": contentHindi,
            "excerpt": excerpt,
            "excerptHindi": excerptHindi,
            "category": category,
            "tags": parsed_tags,
            "author": author,
            "coverImage": cover_image_url,
            "isPublished": True,
            "views": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = blogs_col.insert_one(blog_doc)
        blog_doc["_id"] = result.inserted_id
        return serialize_doc(blog_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{blog_id}")
async def update_blog(
    blog_id: str,
    title: Optional[str] = Form(None),
    titleHindi: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    contentHindi: Optional[str] = Form(None),
    excerpt: Optional[str] = Form(None),
    excerptHindi: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    coverImage: Optional[UploadFile] = File(None),
    admin_payload: dict = Depends(get_current_admin)
):
    blogs_col = get_collection("blogs")
    try:
        if not ObjectId.is_valid(blog_id):
            raise HTTPException(status_code=400, detail="Invalid blog ID")
            
        existing = blogs_col.find_one({"_id": ObjectId(blog_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Not found")
            
        updates = {"updatedAt": datetime.utcnow()}
        if title is not None: updates["title"] = title
        if titleHindi is not None: updates["titleHindi"] = titleHindi
        if content is not None: updates["content"] = content
        if contentHindi is not None: updates["contentHindi"] = contentHindi
        if excerpt is not None: updates["excerpt"] = excerpt
        if excerptHindi is not None: updates["excerptHindi"] = excerptHindi
        if category is not None: updates["category"] = category
        if author is not None: updates["author"] = author
        
        if tags is not None:
            try:
                updates["tags"] = json.loads(tags)
            except Exception:
                pass
                
        if coverImage and coverImage.filename:
            ext = os.path.splitext(coverImage.filename)[1]
            filename = f"blog_{int(time.time() * 1000)}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            content_bytes = await coverImage.read()
            with open(filepath, "wb") as f:
                f.write(content_bytes)
            updates["coverImage"] = f"/blog-images/{filename}"
            
        blogs_col.update_one({"_id": ObjectId(blog_id)}, {"$set": updates})
        updated = blogs_col.find_one({"_id": ObjectId(blog_id)})
        return serialize_doc(updated)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{blog_id}")
def delete_blog(blog_id: str, admin_payload: dict = Depends(get_current_admin)):
    blogs_col = get_collection("blogs")
    try:
        if not ObjectId.is_valid(blog_id):
            raise HTTPException(status_code=400, detail="Invalid blog ID")
        result = blogs_col.delete_one({"_id": ObjectId(blog_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return {"message": "Deleted"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
