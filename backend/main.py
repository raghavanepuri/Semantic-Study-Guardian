import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

# Import the strict models you just provided
from models import WebPageRequest, ClassificationResponse

app = FastAPI(title="Semantic Study Guardian Backend")

# Enable CORS so your local Chrome extension can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_TUNNEL_URL = "http://localhost:44543/api/generate"
MODEL_NAME = "qwen3" 

@app.post("/classify", response_model=ClassificationResponse)
async def classify_page(request: WebPageRequest):
    # Format the dictionary of meta tags into a readable string for the LLM
    meta_tags_str = ", ".join([f"{k}: {v}" for k, v in request.meta_tags.items()])
    
    # Format the optional transcript if it exists
    transcript_str = request.transcript if request.transcript else "No transcript available."

    # The single prompt enforcing the exact two-layer architecture
    # It forces the LLM to output a raw JSON structure so we can populate ClassificationResponse perfectly
    prompt = f"""
    You are an academic guardian assistant. Analyze the web page data below and determine if the user should be allowed to view it based on their study goal.
    
    USER'S STUDY GOAL: "{request.study_goal}"
    
    CURRENT WEB PAGE DETAILS:
    - URL: {request.url}
    - Title: {request.title}
    - Meta Tags: {meta_tags_str}
    - Visible Page Text (Snippet): {request.visible_text[:1500]}
    - Video Transcript (if applicable): {transcript_str[:1500]}
    
    CLASSIFICATION STEPS (LAYERED ARCHITECTURE):
    1. First, evaluate if this is a general "HOMEPAGE" or a "SEARCH_PAGE". If it is, immediately set decision to "ALLOW", page_type to "HOMEPAGE" or "SEARCH_PAGE", and provide a brief reason.
    2. If it is a specific article, video, or content page ("CONTENT_PAGE"), evaluate whether the visible text or transcript aligns with the user's study goal. If it is relevant, set decision to "ALLOW". If it is a distraction or irrelevant, set decision to "BLOCK".
    
    OUTPUT FORMAT:
    You must respond ONLY with a raw valid JSON object. Do not wrap it in markdown code blocks. Do not write any explanations outside the JSON.
    
    Expected JSON Structure:
    {{
        "decision": "ALLOW" or "BLOCK",
        "reason": "A brief explanation of your classification decision.",
        "confidence": 0.0 to 1.0,
        "page_type": "HOMEPAGE", "SEARCH_PAGE", or "CONTENT_PAGE"
    }}
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        # Send payload through the local end of the SSH tunnel
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(OLLAMA_TUNNEL_URL, json=payload)
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to communicate with remote Ollama engine.")
            
            result_json = response.json()
            raw_llm_text = result_json.get("response", "").strip()
            
            # Parse the clean JSON response out of the LLM output
            try:
                parsed_response = json.loads(raw_llm_text)
                
                # Return data strictly structured as a ClassificationResponse
                return ClassificationResponse(
                    decision=parsed_response.get("decision", "ALLOW").upper(),
                    reason=parsed_response.get("reason", "Fallback default decision."),
                    confidence=float(parsed_response.get("confidence", 0.5)),
                    page_type=parsed_response.get("page_type", "CONTENT_PAGE").upper()
                )
            except (json.JSONDecodeError, ValueError) as parse_err:
                # Fallback implementation if the LLM output deviates from formatting instructions
                fallback_decision = "BLOCK" if "BLOCK" in raw_llm_text.upper() else "ALLOW"
                return ClassificationResponse(
                    decision=fallback_decision,
                    reason="Parsed from unformatted model output stream.",
                    confidence=0.5,
                    page_type="CONTENT_PAGE"
                )
            
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"SSH Tunnel connection error: {exc}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "location": "local_laptop"}