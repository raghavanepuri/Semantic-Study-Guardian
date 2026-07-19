from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from backend.models import WebPageRequest, ClassificationResponse

app = FastAPI(
    title="Semantic Study Guardian",
    description="Production backend routing extension requests to the remote Qwen LLM.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama local endpoint configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3:4b"  # Swap to "qwen2.5-coder:7b" later if you want to experiment!

@app.get("/")
def health_check():
    return {"status": "ok", "message": f"Server running. Model set to {MODEL_NAME}"}

@app.post("/classify", response_model=ClassificationResponse)
async def classify_webpage(request: WebPageRequest):
    url_lower = request.url.lower()
    
    # Fast path: Skip LLM processing for bare homepages or search URLs to reduce latency
    if url_lower.endswith("/") or "search" in url_lower or "results" in url_lower:
        return ClassificationResponse(
            decision="ALLOW",
            reason="Navigation/search page automatically bypassed.",
            confidence=1.0,
            page_type="NAVIGATION"
        )
        
    # Build a strict prompt forcing the LLM to think like a classifier
    prompt = f"""
    You are an absolute, strict academic firewall called the Semantic Study Guardian.
    Your task is to analyze if a webpage is relevant to the user's current active study goal.
    
    CRITERIA:
    - If the webpage content directly helps, informs, or contributes to achieving the study goal, output ALLOW.
    - If the webpage content is social media, entertainment, general news, or completely unrelated to the goal, output BLOCK.
    
    INPUT DATA:
    - Current Study Goal: {request.study_goal}
    - Page Title: {request.title}
    - Snippet of Page Text: {request.visible_text[:800]}
    
    OUTPUT FORMAT:
    You must respond with exactly two lines. Do not include any markdown formatting, asterisks, or extra sentences.
    Line 1: Either ALLOW or BLOCK
    Line 2: A short, single-sentence reason for the decision.
    """

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            })
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Ollama internal error")
                
            result_json = response.json()
            raw_text = result_json.get("response", "").strip()
            
            # Parse the strict two-line output structure
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
            
            decision = "BLOCK"
            reason = "Failed to parse model decision safely."
            
            if len(lines) >= 1:
                decision = "ALLOW" if "ALLOW" in lines[0].upper() else "BLOCK"
            if len(lines) >= 2:
                reason = lines[1]
            elif len(lines) == 1:
                reason = "Evaluated by Qwen LLM engine."

            return ClassificationResponse(
                decision=decision,
                reason=reason,
                confidence=0.85,
                page_type="CONTENT_PAGE"
            )

        except httpx.RequestError as e:
            # Fallback strategy if the LLM cluster gets heavily congested
            return ClassificationResponse(
                decision="ALLOW",
                reason=f"Cluster fallback safety engaged. Error: {str(e)}",
                confidence=0.50,
                page_type="FALLBACK"
            )