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

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    "https://127.0.0.1:3000",
    "https://eiaa-next.vercel.app/",  
    "https://eiaa-next.vercel.app",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint"""
    return {"status": "online", "message": "EIAA Backend API is running"}


app.include_router(upload_router)