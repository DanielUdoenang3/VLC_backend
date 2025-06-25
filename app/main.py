from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router.auth import user_router
from app.services.auth import initialize_firebase
from app.utils.settings import settings
from contextlib import asynccontextmanager


FE_URL=settings.FE_URL
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup event triggered. Initializing Firebase...")
    initialize_firebase()
    print("Firebase initialization complete.")
    yield
    print("Application shutdown event triggered.")
    
app = FastAPI(lifespan=lifespan)
# CORS settings
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    f"{FE_URL}"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{FE_URL}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to VLC-Backend API"}