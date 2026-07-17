from pydantic import BaseModel
from typing import Dict, Optional


class WebPageRequest(BaseModel):
    """
    Schema for the incoming webpage classification request.
    This is what the Chrome extension will send to our backend.
    """
    study_goal: str
    title: str
    url: str
    meta_tags: Dict[str, str]
    content_preview: Optional[str] = None


class ClassificationResponse(BaseModel):
    """
    Schema for what our backend returns to the Chrome extension.
    """
    decision: str  # "ALLOW" or "BLOCK"
    reason: str
    confidence: float  # 0.0 to 1.0
    page_type: Optional[str] = None  # "HOMEPAGE", "SEARCH_RESULTS", "CONTENT"