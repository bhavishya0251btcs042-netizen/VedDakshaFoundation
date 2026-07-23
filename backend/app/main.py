import os
import sys

# Ensure backend folder is in sys.path so 'app' imports work from any working directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime

from app.config import Config
from app.database import check_db_connection, get_collection
from app.routes import auth, events, donations, blog, gallery, contact, volunteer, connections

# Initialize FastAPI App with prefix /api
app = FastAPI(title="Ved Daksha Foundation API", docs_url="/docs", redoc_url="/redoc")

# CORS Setup
origins = [Config.FRONTEND_URL] if Config.FRONTEND_URL and Config.FRONTEND_URL != "*" else ["*"]
# If Config.FRONTEND_URL is "*", origins should just be ["*"]
if "*" in origins:
    origins = ["*"]
else:
    # Allow local file access (origin "null") and local development hosts
    local_origins = [
        "null",
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://veddakshafoundation-production.up.railway.app",
    ]
    for lo in local_origins:
        if lo not in origins:
            origins.append(lo)

# Always include null origin for file:// access during development
if "*" not in origins and "null" not in origins:
    origins.append("null")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"],
)

# Custom middleware to handle null origin (file:// protocol) explicitly
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

class NullOriginCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        origin = request.headers.get("origin", "")
        if origin == "null" or not origin:
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
        return response

app.add_middleware(NullOriginCORSMiddleware)

# ── Ensure uploads directories exist ──
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_EVENTS_DIR = os.path.join(BACKEND_DIR, "uploads", "events")
UPLOAD_BLOG_DIR = os.path.join(BACKEND_DIR, "uploads", "blog")
IMAGES_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "images")

os.makedirs(UPLOAD_EVENTS_DIR, exist_ok=True)
os.makedirs(UPLOAD_BLOG_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
UPLOAD_RESUMES_DIR = os.path.join(BACKEND_DIR, "uploads", "resumes")
os.makedirs(UPLOAD_RESUMES_DIR, exist_ok=True)
UPLOAD_CONNECTIONS_DIR = os.path.join(BACKEND_DIR, "uploads", "connections")
os.makedirs(UPLOAD_CONNECTIONS_DIR, exist_ok=True)
UPLOAD_GALLERY_DIR = os.path.join(BACKEND_DIR, "uploads", "gallery")
os.makedirs(UPLOAD_GALLERY_DIR, exist_ok=True)

# ── Mount Static Folders ──
app.mount("/uploads", StaticFiles(directory=IMAGES_DIR), name="uploads")
app.mount("/event-images", StaticFiles(directory=UPLOAD_EVENTS_DIR), name="event-images")
app.mount("/blog-images", StaticFiles(directory=UPLOAD_BLOG_DIR), name="blog-images")
app.mount("/resumes", StaticFiles(directory=UPLOAD_RESUMES_DIR), name="resumes")
app.mount("/connection-images", StaticFiles(directory=UPLOAD_CONNECTIONS_DIR), name="connection-images")
app.mount("/gallery-images", StaticFiles(directory=UPLOAD_GALLERY_DIR), name="gallery-images")

# ── Include Routers ──
app.include_router(auth.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(donations.router, prefix="/api")
app.include_router(blog.router, prefix="/api")
app.include_router(gallery.router, prefix="/api")
app.include_router(contact.router, prefix="/api")
app.include_router(volunteer.router, prefix="/api")
app.include_router(connections.router, prefix="/api")

@app.on_event("startup")
def seed_database():
    try:
        if not check_db_connection():
            print("[WARNING] Skipping seeding: database not connected.")
            return

        # 0. Seed default admin user if missing
        try:
            admins_col = get_collection("admins")
            if admins_col.count_documents({}) == 0:
                print("Seeding default admin user...")
                from app.utils import hash_password
                hashed = hash_password(Config.ADMIN_PASSWORD)
                admin_doc = {
                    "email": Config.ADMIN_EMAIL.strip().lower(),
                    "password": hashed,
                    "name": "Dr. Usha Tyagi",
                    "createdAt": datetime.utcnow()
                }
                admins_col.insert_one(admin_doc)
                print(f"Default admin user created: {Config.ADMIN_EMAIL}")
        except Exception as ae:
            print(f"Admin seeding warning: {ae}")

        # 1. Seed connections
        conn_col = get_collection("connections")
        if conn_col.count_documents({}) == 0:  # seed default connections if none exist
            print("Seeding default connections...")
            default_connections = [
                {
                    "name": "Dr. Usha Tyagi",
                    "role": "Founder & President",
                    "bio": "The driving force behind Ved Daksha Foundation. Dr. Usha Tyagi has dedicated years to providing free education to underprivileged children of Ghaziabad.",
                    "imageUrl": "/images/1000087600.jpg.jpeg",
                    "order": 1,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Vishakha Tyagi",
                    "role": "Program Head & Anchor",
                    "bio": "Vishakha leads daily programs and serves as the main event anchor, coordinating classes, events, and volunteer management.",
                    "imageUrl": "/images/1000179545.jpg.jpeg",
                    "order": 2,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Dr. Richa Sood",
                    "role": "Education Advisor",
                    "bio": "A respected educationist and author, Dr. Richa Sood advises on curriculum and has been a keynote presence at the foundation's annual events.",
                    "imageUrl": "/images/1000179518.jpg.jpeg",
                    "order": 3,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Aryan Tyagi",
                    "role": "Youth Coordinator",
                    "bio": "Aryan bridges the gap between the foundation and younger volunteers, organizing youth participation in outreach events.",
                    "imageUrl": "/images/1000179580.jpg.jpeg",
                    "order": 4,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Dr. Preeti Sharma",
                    "role": "Medical Advisor",
                    "bio": "Dr. Preeti Sharma brings medical expertise and community health support to the foundation, overseeing health camps and wellness programs.",
                    "imageUrl": "/images/1000179574.jpg.jpeg",
                    "order": 5,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Volunteer Team",
                    "role": "Educators & Coaches",
                    "bio": "Young educators, dance teachers, yoga instructors who show up every day to make a difference.",
                    "imageUrl": "/images/1000179556.jpg.jpeg",
                    "order": 6,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            ]
            conn_col.insert_many(default_connections)

        # 2. Seed gallery
        gal_col = get_collection("gallery")
        if gal_col.count_documents({}) < 10:  # re-seed if partial/empty
            print("Seeding default gallery images (all 41 images)...")
            default_gallery = [
                {"url": "/images/1000179556.jpg.jpeg", "caption": "Annual Felicitation Event", "occasion": "Annual Felicitation Event", "category": "general", "order": 1, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087433.jpg.jpeg", "caption": "Yoga Performance", "occasion": "Yoga Performance", "category": "general", "order": 2, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087283.jpg.jpeg", "caption": "Dance Showcase", "occasion": "Dance Showcase", "category": "general", "order": 3, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179500.jpg.jpeg", "caption": "School Bag Distribution", "occasion": "School Bag Distribution", "category": "general", "order": 4, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087355.jpg.jpeg", "caption": "Medal Ceremony", "occasion": "Medal Ceremony", "category": "general", "order": 5, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087516.jpg.jpeg", "caption": "Award Ceremony", "occasion": "Award Ceremony", "category": "general", "order": 6, "createdAt": datetime.utcnow()},
                {"url": "/images/1000086482.jpg.jpeg", "caption": "Our Children", "occasion": "Our Children", "category": "general", "order": 7, "createdAt": datetime.utcnow()},
                {"url": "/images/1000086223.jpg.jpeg", "caption": "Foundation Activity", "occasion": "Foundation Activity", "category": "general", "order": 8, "createdAt": datetime.utcnow()},
                {"url": "/images/1000086285.jpg.jpeg", "caption": "Children Learning", "occasion": "Children Learning", "category": "general", "order": 9, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087227.jpg.jpeg", "caption": "Cultural Program", "occasion": "Cultural Program", "category": "general", "order": 10, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087237.jpg.jpeg", "caption": "Special Event", "occasion": "Special Event", "category": "general", "order": 11, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087243.jpg.jpeg", "caption": "Student Achievement", "occasion": "Student Achievement", "category": "general", "order": 12, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087271.jpg.jpeg", "caption": "Yoga & Wellness", "occasion": "Yoga & Wellness", "category": "general", "order": 13, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087287.jpg.jpeg", "caption": "Dance Performance", "occasion": "Dance Performance", "category": "general", "order": 14, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087293.jpg.jpeg", "caption": "Community Gathering", "occasion": "Community Gathering", "category": "general", "order": 15, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087405.jpg.jpeg", "caption": "Educational Session", "occasion": "Educational Session", "category": "general", "order": 16, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087407.jpg.jpeg", "caption": "Volunteer Activity", "occasion": "Volunteer Activity", "category": "general", "order": 17, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087431.jpg.jpeg", "caption": "Community Outreach", "occasion": "Community Outreach", "category": "general", "order": 18, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087479.jpg.jpeg", "caption": "Foundation Celebration", "occasion": "Foundation Celebration", "category": "general", "order": 19, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087481.jpg.jpeg", "caption": "Annual Event", "occasion": "Annual Event", "category": "general", "order": 20, "createdAt": datetime.utcnow()},
                {"url": "/images/1000087600.jpg.jpeg", "caption": "Leadership & Guidance", "occasion": "Leadership & Guidance", "category": "general", "order": 21, "createdAt": datetime.utcnow()},
                {"url": "/images/1000106069.jpg.jpeg", "caption": "Children's Activities", "occasion": "Children's Activities", "category": "general", "order": 22, "createdAt": datetime.utcnow()},
                {"url": "/images/1000106080.jpg.jpeg", "caption": "Health Camp", "occasion": "Health Camp", "category": "general", "order": 23, "createdAt": datetime.utcnow()},
                {"url": "/images/1000115293.jpg.jpeg", "caption": "Special Occasion", "occasion": "Special Occasion", "category": "general", "order": 24, "createdAt": datetime.utcnow()},
                {"url": "/images/1000178048.jpg.jpeg", "caption": "Foundation Moments", "occasion": "Foundation Moments", "category": "general", "order": 25, "createdAt": datetime.utcnow()},
                {"url": "/images/1000178984.jpg.jpeg", "caption": "Training Session", "occasion": "Training Session", "category": "general", "order": 26, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179051.jpg.jpeg", "caption": "Community Service", "occasion": "Community Service", "category": "general", "order": 27, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179314.jpg.jpeg", "caption": "Youth Empowerment", "occasion": "Youth Empowerment", "category": "general", "order": 28, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179412.jpg.jpeg", "caption": "Skill Development", "occasion": "Skill Development", "category": "general", "order": 29, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179494.jpg.jpeg", "caption": "Education for All", "occasion": "Education for All", "category": "general", "order": 30, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179518.jpg.jpeg", "caption": "Advisors & Mentors", "occasion": "Advisors & Mentors", "category": "general", "order": 31, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179545.jpg.jpeg", "caption": "Program Coordination", "occasion": "Program Coordination", "category": "general", "order": 32, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179574.jpg.jpeg", "caption": "Medical Outreach", "occasion": "Medical Outreach", "category": "general", "order": 33, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179580.jpg.jpeg", "caption": "Youth Volunteers", "occasion": "Youth Volunteers", "category": "general", "order": 34, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179703.jpg.jpeg", "caption": "Celebration & Joy", "occasion": "Celebration & Joy", "category": "general", "order": 35, "createdAt": datetime.utcnow()},
                {"url": "/images/1000179906.jpg.jpeg", "caption": "Cultural Heritage", "occasion": "Cultural Heritage", "category": "general", "order": 36, "createdAt": datetime.utcnow()},
                {"url": "/images/1000191716.jpg.jpeg", "caption": "Foundation Events", "occasion": "Foundation Events", "category": "general", "order": 37, "createdAt": datetime.utcnow()},
                {"url": "/images/1000191718.jpg.jpeg", "caption": "Community Programs", "occasion": "Community Programs", "category": "general", "order": 38, "createdAt": datetime.utcnow()},
                {"url": "/images/1000191720.jpg.jpeg", "caption": "Learning Together", "occasion": "Learning Together", "category": "general", "order": 39, "createdAt": datetime.utcnow()},
                {"url": "/images/1000191722.jpg.jpeg", "caption": "Inspiring Stories", "occasion": "Inspiring Stories", "category": "general", "order": 40, "createdAt": datetime.utcnow()},
                {"url": "/images/1000252075.jpg.jpeg", "caption": "Making a Difference", "occasion": "Making a Difference", "category": "general", "order": 41, "createdAt": datetime.utcnow()},
            ]
            gal_col.insert_many(default_gallery)

        # 3. Seed blogs
        blogs_col = get_collection("blogs")
        if blogs_col.count_documents({}) == 0:
            print("Seeding default blogs...")
            default_blogs = [
                {
                    "title": "How Free Education Changes a Child's Trajectory in Ghaziabad",
                    "titleHindi": "गाजियाबाद में मुफ्त शिक्षा कैसे एक बच्चे के भविष्य को बदलती है",
                    "slug": "how-free-education-changes-child-trajectory-ghaziabad",
                    "content": "When a child from a daily-wage family gets access to books, a classroom, and a caring teacher — everything changes. At Ved Daksha Foundation, we see this transformation every single day. Children who were once out of school are now reading, writing, and dreaming of careers...",
                    "contentHindi": "जब दैनिक मजदूरी करने वाले परिवार के किसी बच्चे को किताबों, एक कक्षा और एक स्नेही शिक्षक तक पहुँच मिलती है - तो सब कुछ बदल जाता है। वेद दक्षा फाउंडेशन में, हम हर दिन इस बदलाव को देखते हैं। जो बच्चे कभी स्कूल से बाहर थे, वे अब पढ़ रहे हैं, लिख रहे हैं और अपने करियर का सपना देख रहे हैं...",
                    "excerpt": "When a child from a daily-wage family gets access to books, a classroom, and a caring teacher — everything changes.",
                    "excerptHindi": "जब दैनिक मजदूरी करने वाले परिवार के किसी बच्चे को किताबों, एक कक्षा और एक स्नेही शिक्षक तक पहुँच मिलती है - तो सब कुछ बदल जाता है।",
                    "category": "Education",
                    "tags": ["education", "children", "ghaziabad"],
                    "author": "Dr. Usha Tyagi",
                    "coverImage": "/images/1000086285.jpg.jpeg",
                    "isPublished": True,
                    "views": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "title": "Why Yoga and Dance Are as Important as Textbooks",
                    "titleHindi": "योग और नृत्य पाठ्यपुस्तकों की तरह ही क्यों महत्वपूर्ण हैं",
                    "slug": "why-yoga-dance-important-textbooks",
                    "content": "Physical expression, discipline, and artistry are not extracurricular — they are the core of holistic childhood development. When our children perform yoga and dance on stage, they're not just performing — they're proving to themselves and the world that they are capable of excellence...",
                    "contentHindi": "शारीरिक अभिव्यक्ति, अनुशासन और कलात्मकता अतिरिक्त गतिविधियाँ नहीं हैं - वे समग्र बाल विकास का मूल हैं। जब हमारे बच्चे मंच पर योग और नृत्य करते हैं, तो वे केवल प्रदर्शन नहीं कर रहे होते हैं - वे खुद को और दुनिया को साबित कर रहे होते हैं कि वे उत्कृष्टता के सक्षम हैं...",
                    "excerpt": "Physical expression, discipline, and artistry are not extracurricular — they are the core of holistic childhood development.",
                    "excerptHindi": "शारीरिक अभिव्यक्ति, अनुशासन और कलात्मकता अतिरिक्त गतिविधियाँ नहीं हैं - वे समग्र बाल विकास का मूल हैं।",
                    "category": "Arts & Development",
                    "tags": ["yoga", "dance", "development"],
                    "author": "Dr. Usha Tyagi",
                    "coverImage": "/images/1000087271.jpg.jpeg",
                    "isPublished": True,
                    "views": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "title": "5 Ways You Can Support Underprivileged Children Without Donating Money",
                    "titleHindi": "बिना पैसे दान किए वंचित बच्चों की मदद करने के 5 तरीके",
                    "slug": "5-ways-support-underprivileged-children-without-money",
                    "content": "Books, time, skills, connections, and presence. There are more ways to give than you think. Our volunteers prove this every week — some teach English, others organise health camps, and some simply show up to cheer our children at performances...",
                    "contentHindi": "किताबें, समय, कौशल, संपर्क और उपस्थिति। आपके सोचने से भी अधिक दान देने के तरीके हैं। हमारे स्वयंसेवक हर हफ्ते इसे साबित करते हैं - कुछ अंग्रेजी सिखाते हैं, अन्य स्वास्थ्य शिविर आयोजित करते हैं, और कुछ केवल प्रदर्शनों में हमारे बच्चों का उत्साह बढ़ाने के लिए आते हैं...",
                    "excerpt": "Books, time, skills, connections, and presence. There are more ways to give than you think.",
                    "excerptHindi": "किताबें, समय, कौशल, संपर्क और उपस्थिति। आपके सोचने से भी अधिक दान देने के तरीके हैं।",
                    "category": "Community",
                    "tags": ["volunteer", "support", "community"],
                    "author": "Dr. Usha Tyagi",
                    "coverImage": "/images/1000087355.jpg.jpeg",
                    "isPublished": True,
                    "views": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            ]
            blogs_col.insert_many(default_blogs)

    except Exception as e:
        print(f"[WARNING] Database seeding failed: {e}")

@app.get("/api/health")
def health_check():
    db_connected = check_db_connection()
    return {
        "status": "ok" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "time": datetime.utcnow().isoformat()
    }

# ── Serve Frontend Files ──
FRONTEND_DIR = os.path.dirname(BACKEND_DIR)

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/index.html")
def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/blog")
def read_blog_clean():
    return FileResponse(os.path.join(FRONTEND_DIR, "blog.html"))

@app.get("/blog.html")
def read_blog():
    return FileResponse(os.path.join(FRONTEND_DIR, "blog.html"))

# Mount admin and images directories
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/admin", StaticFiles(directory=os.path.join(FRONTEND_DIR, "admin"), html=True), name="admin")

from fastapi.responses import Response

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # Return a 1x1 transparent ICO to stop 404 spam
    # Minimal valid .ico file (1x1 pixel, transparent)
    ico_bytes = bytes([
        0,0,1,0,1,0,1,1,0,0,1,0,24,0,40,0,0,0,
        40,0,0,0,1,0,0,0,2,0,0,0,1,0,24,0,0,0,0,0,
        4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,255,0,0,0,0,0,0,0,0,0,0,0
    ])
    return Response(content=ico_bytes, media_type="image/x-icon")
