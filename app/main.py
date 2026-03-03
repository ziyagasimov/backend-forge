from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db_models import init_db
from app.auth import app as auth_app
from app.team_project import router as team_project_router
from app.task import router as task_router
from app.file_upload import router as file_upload_router

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

# Include routers
app.include_router(team_project_router, tags=["Teams & Projects"])
app.include_router(task_router, tags=["Tasks"])
app.include_router(file_upload_router, tags=["Files"])

# Mount auth endpoints directly
from app.auth import register, login, read_users_me, admin_endpoint
app.post("/register")(register)
app.post("/token")(login)
app.get("/me")(read_users_me)
app.get("/admin")(admin_endpoint)

@app.get("/")
def root():
    return {"message": "IdeaForge AI Backend is running!"}
