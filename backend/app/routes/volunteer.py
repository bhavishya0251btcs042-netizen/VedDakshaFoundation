import os
import time
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Request
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.database import get_collection
from app.models import VolunteerConfigUpdate, VolunteerEmailSend
from app.utils import serialize_doc, serialize_docs, send_custom_email
from app.middleware import get_current_admin
from app.resume_parser import parse_resume

router = APIRouter(prefix="/volunteer", tags=["volunteer"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DEFAULT_FIELDS = [
    { "id": "name", "label": "Full Name", "labelHindi": "पूरा नाम", "type": "text", "required": True, "enabled": True },
    { "id": "email", "label": "Email Address", "labelHindi": "ईमेल", "type": "email", "required": True, "enabled": True },
    { "id": "phone", "label": "Phone Number", "labelHindi": "फ़ोन नंबर", "type": "tel", "required": True, "enabled": True },
    { "id": "occupation", "label": "Occupation", "labelHindi": "पेशा", "type": "text", "required": False, "enabled": True },
    { "id": "organization", "label": "School / College / Organization", "labelHindi": "संस्था", "type": "text", "required": False, "enabled": True },
    { "id": "field_of_interest", "label": "Field of Interest", "labelHindi": "रुचि का क्षेत्र", "type": "select", "required": True, "enabled": True, "options": [
      "Education / शिक्षा",
      "Yoga & Self-Defence / योग और आत्म-रक्षा",
      "Art & Music / कला और संगीत",
      "Health Camps / स्वास्थ्य शिविर",
      "Management / प्रबंधन"
    ] },
    { "id": "message", "label": "Why do you want to volunteer?", "labelHindi": "आप स्वयंसेवक क्यों बनना चाहते हैं?", "type": "textarea", "required": False, "enabled": True },
    { "id": "feedback", "label": "Feedback / Suggestions", "labelHindi": "प्रतिक्रिया / सुझाव", "type": "textarea", "required": False, "enabled": True }
]

def get_db_config():
    config_col = get_collection("volunteer_config")
    cfg = config_col.find_one({"_id": "default_config"})
    if not cfg:
        cfg = {"_id": "default_config", "fields": DEFAULT_FIELDS}
        config_col.insert_one(cfg)
    else:
        existing_ids = [f["id"] for f in cfg.get("fields", [])]
        if "feedback" not in existing_ids:
            cfg["fields"].append({
                "id": "feedback",
                "label": "Feedback / Suggestions",
                "labelHindi": "प्रतिक्रिया / सुझाव",
                "type": "textarea",
                "required": False,
                "enabled": True
            })
            config_col.update_one({"_id": "default_config"}, {"$set": {"fields": cfg["fields"]}})
    return cfg

@router.get("/config")
def get_volunteer_config():
    try:
        cfg = get_db_config()
        return serialize_doc(cfg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
def update_volunteer_config(data: VolunteerConfigUpdate, admin_payload: dict = Depends(get_current_admin)):
    config_col = get_collection("volunteer_config")
    try:
        # Convert Pydantic fields list to dictionary list
        fields_list = [f.dict() for f in data.fields]
        result = config_col.update_one(
            {"_id": "default_config"},
            {"$set": {"fields": fields_list}},
            upsert=True
        )
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply")
async def volunteer_apply(request: Request, resume: Optional[UploadFile] = File(None)):
    volunteers_col = get_collection("volunteers")
    try:
        form_data = await request.form()
        cfg = get_db_config()
        fields = cfg.get("fields", DEFAULT_FIELDS)
        
        # Build the document dynamically
        app_doc = {}
        custom_fields = {}
        
        # Validate and extract configured fields
        for field in fields:
            fid = field["id"]
            if field["type"] == "checkbox":
                val = form_data.getlist(fid)
            else:
                val = form_data.get(fid)
            
            if field["enabled"]:
                # Check for file field validation separately
                if field["type"] == "file":
                    if field["required"] and (not resume or not resume.filename):
                        raise HTTPException(status_code=400, detail="Resume file is required / बायोडाटा फ़ाइल आवश्यक है")
                else:
                    if field["required"] and not val:
                        raise HTTPException(status_code=400, detail=f"Field '{field['label']}' is required / '{field['label']}' आवश्यक है")
                    
                    # Store standard fields directly, custom fields in customFields dict
                    if fid in ["name", "email", "phone", "occupation", "organization", "field_of_interest", "message", "feedback"]:
                        app_doc[fid] = val if val is not None else ""
                    else:
                        custom_fields[fid] = val if val is not None else ""

        # Save resume file if provided
        resume_url = ""
        if resume and resume.filename:
            ext = os.path.splitext(resume.filename)[1]
            filename = f"resume_{int(time.time() * 1000)}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            content_bytes = await resume.read()
            with open(filepath, "wb") as f:
                f.write(content_bytes)
            resume_url = f"/resumes/{filename}"

        # Setup standard document fields
        app_doc["resumeUrl"] = resume_url
        app_doc["customFields"] = custom_fields
        app_doc["status"] = "pending"
        app_doc["createdAt"] = datetime.utcnow()
        
        # Insert document
        volunteers_col.insert_one(app_doc)
        return {"message": "Application submitted successfully! / आवेदन सफलतापूर्वक जमा किया गया!"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications")
def get_volunteer_applications(admin_payload: dict = Depends(get_current_admin)):
    volunteers_col = get_collection("volunteers")
    try:
        cursor = volunteers_col.find({}).sort("createdAt", -1).limit(100)
        apps = list(cursor)
        return serialize_docs(apps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/applications/{app_id}/status")
def update_application_status(app_id: str, status: str, admin_payload: dict = Depends(get_current_admin)):
    volunteers_col = get_collection("volunteers")
    try:
        if not ObjectId.is_valid(app_id):
            raise HTTPException(status_code=400, detail="Invalid application ID")
            
        result = volunteers_col.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": {"status": status}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Application not found")
            
        return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/{app_id}/email")
def send_email_to_volunteer(app_id: str, email_data: VolunteerEmailSend, admin_payload: dict = Depends(get_current_admin)):
    volunteers_col = get_collection("volunteers")
    try:
        if not ObjectId.is_valid(app_id):
            raise HTTPException(status_code=400, detail="Invalid application ID")
            
        app_doc = volunteers_col.find_one({"_id": ObjectId(app_id)})
        if not app_doc:
            raise HTTPException(status_code=404, detail="Application not found")
            
        to_email = app_doc.get("email")
        if not to_email:
            raise HTTPException(status_code=400, detail="Applicant has no email address")

        # HTML formatting template
        html_content = f"""<div style="font-family:sans-serif;max-width:600px;color:#333;line-height:1.6">
          <div style="background:#1B6B3A;padding:20px;text-align:center;border-radius:6px 6px 0 0">
            <h2 style="color:#ffffff;margin:0">Ved Daksha Foundation</h2>
          </div>
          <div style="padding:24px;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 6px 6px">
            {email_data.body.replace(chr(10), '<br>')}
          </div>
          <div style="text-align:center;font-size:12px;color:#888;margin-top:20px">
            Ved Daksha Foundation · Ghaziabad · Delhi · Meerut
          </div>
        </div>"""
        
        send_custom_email(to_email, email_data.subject, html_content)
        return {"message": f"Email successfully sent to {to_email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/{app_id}/analyze")
def analyze_applicant_resume(app_id: str, force: bool = False, admin_payload: dict = Depends(get_current_admin)):
    volunteers_col = get_collection("volunteers")
    try:
        if not ObjectId.is_valid(app_id):
            raise HTTPException(status_code=400, detail="Invalid application ID")
            
        app_doc = volunteers_col.find_one({"_id": ObjectId(app_id)})
        if not app_doc:
            raise HTTPException(status_code=404, detail="Application not found")

        # Return cached result unless force=true is requested
        if "analysis" in app_doc and not force:
            return app_doc["analysis"]
            
        resume_url = app_doc.get("resumeUrl")
        if not resume_url:
            raise HTTPException(status_code=400, detail="Applicant has not uploaded a resume")
            
        filename = os.path.basename(resume_url)
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Resume file not found on server")
            
        analysis = parse_resume(filepath, default_name=app_doc.get("name", ""))
        
        volunteers_col.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": {"analysis": analysis}}
        )
        
        return analysis
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
