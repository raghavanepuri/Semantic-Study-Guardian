from pydantic import BaseModel
from typing import Dict, Optional

class WebPageRequest(BaseModel):
    """The strict format our Chrome Extension must send."""
    study_goal: str
    url: str
    title: str
    meta_tags: Dict[str, str]
    visible_text: str
    transcript: Optional[str] = None

class ClassificationResponse(BaseModel):
    """The strict format our backend will return to the extension."""
    decision: str  # "ALLOW" or "BLOCK"
    reason: str
    confidence: float
    page_type: Optional[str] = None  # "HOMEPAGE", "SEARCH_PAGE", or "CONTENT_PAGE"