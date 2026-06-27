import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime

from app.config import Config
from app.database import check_db_connection
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
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
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
