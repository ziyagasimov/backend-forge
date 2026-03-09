from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db_models import init_db
from app.auth import app as auth_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    try:
        init_db()
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Database connection error: {e}")
        print("Make sure PostgreSQL is running (docker-compose up -d)")
    yield

app = FastAPI(title="IdeaForge AI Backend", lifespan=lifespan)

# ── CORS middleware ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (Removed redundant PraxisForge routers)

# Mount auth endpoints directly
from app.auth import register, login, read_users_me, admin_endpoint
app.post("/register")(register)
app.post("/token")(login)
app.get("/me")(read_users_me)
app.get("/admin")(admin_endpoint)

@app.get("/")
def root():
    return {"message": "IdeaForge AI Backend is running!"}
