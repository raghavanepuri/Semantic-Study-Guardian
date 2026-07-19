from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models import WebPageRequest, ClassificationResponse

app = FastAPI(
    title="Semantic Study Guardian",
    description="Local development backend for routing extension requests to the LLM.",
    version="1.0.0"
)

# Open the gates so your Chrome extension can communicate with this server locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    """Simple check to ensure the server is alive."""
    return {"status": "ok", "message": "Semantic Study Guardian Backend is running!"}

@app.post("/classify", response_model=ClassificationResponse)
def classify_webpage(request: WebPageRequest):
    """
    Receives webpage metadata from the extension.
    For Day 1, this uses basic dummy logic to prove the network flow works.
    """
    url_lower = request.url.lower()
    title_lower = request.title.lower()
    
    # Heuristic Rule 1: Always allow primary homepages or search patterns
    if url_lower.endswith("/") or "search" in url_lower or "results" in url_lower:
        return ClassificationResponse(
            decision="ALLOW",
            reason="Navigation page (Homepage or Search Results) automatically allowed to prevent tracking friction.",
            confidence=0.99,
            page_type="HOMEPAGE" if url_lower.endswith("/") else "SEARCH_PAGE"
        )
        
    # Heuristic Rule 2: Basic keyword match for testing content pages
    study_goal_lower = request.study_goal.lower()
    if study_goal_lower in title_lower or study_goal_lower in request.visible_text.lower():
        return ClassificationResponse(
            decision="ALLOW",
            reason=f"Content page semantically matches your study goal: '{request.study_goal}'.",
            confidence=0.85,
            page_type="CONTENT_PAGE"
        )
    
    # Default rule if it's content but doesn't match the goal
    return ClassificationResponse(
        decision="BLOCK",
        reason=f"This content page appears unrelated to your primary study goal: '{request.study_goal}'.",
        confidence=0.70,
        page_type="CONTENT_PAGE"
    )