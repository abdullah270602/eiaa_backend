import logging
from fastapi import FastAPI


logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def read_root():
    return {"EIAA Backend": "Online"}


