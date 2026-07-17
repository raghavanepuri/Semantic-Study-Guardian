"""
Semantic Study Guardian Backend
Main FastAPI application
"""

from fastapi import FastAPI
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL
from .models import WebPageRequest, ClassificationResponse
from .llm import llm

app = FastAPI(
    title="Semantic Study Guardian",
    description="LLM-powered webpage classification for focused studying",
    version="0.1.0"
)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Semantic Study Guardian Backend is running",
        "ollama_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL
    }


@app.post("/classify")
def classify(request: WebPageRequest) -> ClassificationResponse:
    """Classify a webpage based on study goal and webpage information."""
    
    # Step 1: Classify page type
    page_type = llm.classify_page_type(
        title=request.title,
        url=request.url,
        meta_tags=request.meta_tags
    )
    
    # Step 2: If navigation page, allow automatically
    if page_type in ["HOMEPAGE", "SEARCH_RESULTS"]:
        return ClassificationResponse(
            decision="ALLOW",
            reason="Navigation page - always allowed",
            confidence=0.99,
            page_type=page_type
        )
    
    # Step 3: Check relevance to study goal
    relevance = llm.classify_relevance(
        study_goal=request.study_goal,
        title=request.title,
        content=request.content_preview or ""
    )
    
    return ClassificationResponse(
        decision=relevance["decision"],
        reason=relevance["reason"],
        confidence=relevance["confidence"],
        page_type=page_type
    )