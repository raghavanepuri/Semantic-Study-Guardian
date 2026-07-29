import json
import logging
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StudyGuardian")

app = FastAPI(title="Semantic Study Guardian API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http_client = httpx.AsyncClient(timeout=30.0)

OLLAMA_URL = "http://127.0.0.1:44543/api/generate"
MODEL_NAME = "qwen3:4b"

class PageData(BaseModel):
    url: str
    title: str
    study_goal: str
    meta_tags: Optional[dict] = {}
    visible_text: Optional[str] = ""

class ClassificationResponse(BaseModel):
    decision: str
    reason: str
    confidence: float
    page_type: str

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["ALLOW", "BLOCK"]},
        "reason": {"type": "string"},
        "confidence": {"type": "number"},
        "page_type": {"type": "string", "enum": ["HOMEPAGE", "SEARCH_PAGE", "CONTENT_PAGE"]}
    },
    "required": ["decision", "reason", "confidence", "page_type"]
}

SYSTEM_PROMPT = """You are an automated web page safety and study-focus classifier.
Your job is to evaluate incoming web traffic dynamically based on the user's active study goal.
You MUST output valid JSON matching the required schema."""

@app.post("/classify", response_model=ClassificationResponse)
async def classify_page(data: PageData):
    meta_tags_str = ", ".join([f"{k}: {v}" for k, v in data.meta_tags.items()]) if data.meta_tags else "None"
    visible_snippet = (data.visible_text[:800] + "...") if data.visible_text and len(data.visible_text) > 800 else (data.visible_text or "None")

    user_prompt = f"""USER STUDY GOAL: "{data.study_goal}"

PAGE DETAILS TO EVALUATE:
- URL: {data.url}
- Title: {data.title}
- Meta Tags: {meta_tags_str}
- Visible Text Snippet: {visible_snippet}

CRITICAL DECISION HIERARCHY (Follow strictly in order):

STEP 1: IS THIS AN ENTRY PORTAL OR SEARCH PAGE?
Check the URL structure. If the page is a home feed, root landing page, or search query page (e.g., URL has no video/article ID, or contains paths like '/', '/results', '/search', 'google.com', 'youtube.com/'):
-> Decision MUST BE "ALLOW".
-> Ignore any recommended video titles or feed text snippets in visible text (home feeds naturally show mixed content, but users need homepages to navigate and search).

STEP 2: IS THIS A SPECIFIC PIECE OF CONTENT?
If the page is a specific video, post, or article (e.g., youtube.com/watch?v=..., blog post, article page):
- IF the specific content subject directly relates to or helps study "{data.study_goal}" -> "ALLOW".
- IF the specific content subject is unrelated entertainment (e.g., movie trailer, gaming, vlog, music video) -> "BLOCK".

Return raw JSON following the schema."""

    logger.info("--- EVALUATING PAGE ---")
    logger.info(f"Target: {data.url} | Goal: {data.study_goal}")

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        "stream": False,
        "format": JSON_SCHEMA,
        "think": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.95
        }
    }

    try:
        response = await http_client.post(OLLAMA_URL, json=payload)
            
        if response.status_code == 200:
            result = response.json()
            raw_response = result.get("response", "").strip()
            
            if raw_response:
                parsed_json = json.loads(raw_response)
                logger.info(f"[LLM DECISION] {parsed_json.get('decision')} | Reason: {parsed_json.get('reason')}")
                
                return ClassificationResponse(
                    decision=parsed_json.get("decision", "BLOCK").upper(),
                    reason=parsed_json.get("reason", "Evaluated by Guardian AI"),
                    confidence=float(parsed_json.get("confidence", 0.9)),
                    page_type=parsed_json.get("page_type", "CONTENT_PAGE")
                )
    except Exception as e:
        logger.error(f"[ERROR] Classification failed: {e}")

    return ClassificationResponse(
        decision="BLOCK",
        reason="Unable to classify page content",
        confidence=0.0,
        page_type="ERROR"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)