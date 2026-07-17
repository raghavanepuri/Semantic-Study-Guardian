"""
Semantic Study Guardian Backend
Main FastAPI application
"""

from fastapi import FastAPI
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL
from .models import WebPageRequest, ClassificationResponse

app = FastAPI(
    title="Semantic Study Guardian",
    description="LLM-powered webpage classification for focused studying",
    version="0.1.0"
)


@app.get("/")
def health_check():
    """
    Health check endpoint.
    Returns: {"status": "ok"} if backend is running.
    """
    return {
        "status": "ok",
        "message": "Semantic Study Guardian Backend is running",
        "ollama_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL
    }


@app.post("/classify")
def classify(request: WebPageRequest) -> ClassificationResponse:
    """
    Classify a webpage based on study goal and webpage information.
    
    Input: WebPageRequest (study_goal, title, url, meta_tags, content_preview)
    Output: ClassificationResponse (decision, reason, confidence, page_type)
    """
    
    # TEMPORARY: Dummy response for testing
    # Later, this will call the actual LLM
    
    dummy_response = ClassificationResponse(
        decision="ALLOW",
        reason="Testing - LLM integration coming next",
        confidence=0.5,
        page_type="CONTENT"
    )
    
    return dummy_response