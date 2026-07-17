from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


from backend.models import WebPage


@app.get("/")
def home():
    return {
        "message": "Semantic Study Guardian Backend is Running!"
    }


@app.post("/classify")
def classify(page: WebPage):
    return {
        "status": "success",
        "received_data": page.model_dump()
    }