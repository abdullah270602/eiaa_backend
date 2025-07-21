import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import router as upload_router
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="EIAA Backend API",
    description="API for EIAA Backend - Upload and Process Files using AI Agents",
)

@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint"""
    return {"status": "online", "message": "EIAA Backend API is running"}


app.include_router(upload_router)