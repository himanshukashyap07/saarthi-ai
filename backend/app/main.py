from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import Base, engine, SessionLocal
from app.db import seed as seed_module
from app.routers import auth, users, goals, recommendations, nudges, chat, staff


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_module.seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

# Wide-open CORS: this is a local hackathon prototype hit from an Expo dev
# client on a phone/emulator over the LAN, not a deployed production service.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(recommendations.router)
app.include_router(nudges.router)
app.include_router(chat.router)
app.include_router(staff.router)
