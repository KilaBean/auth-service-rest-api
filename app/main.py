from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import this
from contextlib import asynccontextmanager

from app.database import Base, engine
from app.routes import auth, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Authentication Service",
    version="2.0.0", # bumped version
    lifespan=lifespan,
)

# --- ADD THIS BLOCK ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[              # In production, list specific domains like ["https://myapp.com"]
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000", # For Swagger
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,      # Essential for HttpOnly Cookies!
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Auth Service is running"}