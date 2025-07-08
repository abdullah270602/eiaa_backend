import logging
from fastapi import FastAPI
from app.routes.upload import router as upload_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def read_root():
    return {"EIAA Backend": "Online"}


app.include_router(upload_router)