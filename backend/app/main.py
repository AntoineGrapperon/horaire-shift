from fastapi import FastAPI
from .database import engine, Base
from . import models

# Create database tables on startup (Simple approach for MVP)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShiftMed API",
    description="Medical Shift Scheduling Platform API",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to ShiftMed API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
