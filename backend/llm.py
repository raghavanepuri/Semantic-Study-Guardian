"""
LLM Interface for Semantic Study Guardian
This module handles all communication with the language model.

Currently uses a dummy implementation for testing.
Later, this will be replaced with real Ollama calls.
"""

from typing import Dict
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL


class LLMClassifier:
    """
    Interface for classifying webpages using an LLM.
    
    This class abstracts away the details of how we talk to the LLM,
    so we can swap implementations without changing the rest of the backend.
    """
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model
    
    def classify_page_type(self, title: str, url: str, meta_tags: Dict[str, str]) -> str:
        """
        Determine if this is a HOMEPAGE, SEARCH_RESULTS, or CONTENT page.
        
        Args:
            title: Webpage title
            url: Webpage URL
            meta_tags: Meta tags from the page
        
        Returns:
            One of: "HOMEPAGE", "SEARCH_RESULTS", "CONTENT"
        """
        
        # TEMPORARY DUMMY IMPLEMENTATION
        # Later, this will build a prompt and call Ollama
        
        # Simple heuristics for testing
        url_lower = url.lower()
        title_lower = title.lower()
        
        if "search" in url_lower or "results" in url_lower:
            return "SEARCH_RESULTS"
        
        if url_lower.endswith("/") or title_lower == "home" or url_lower.count("/") <= 2:
            return "HOMEPAGE"
        
        return "CONTENT"
    
    def classify_relevance(self, study_goal: str, title: str, content: str) -> Dict:
        """
        Determine if webpage is relevant to the study goal.
        
        Args:
            study_goal: Student's current study objective
            title: Webpage title
            content: Webpage content/description
        
        Returns:
            {
                "decision": "ALLOW" or "BLOCK",
                "reason": explanation,
                "confidence": 0.0 to 1.0
            }
        """
        
        # TEMPORARY DUMMY IMPLEMENTATION
        # Later, this will build a prompt and call Ollama
        
        # For now, just check if study goal appears in title
        study_lower = study_goal.lower()
        title_lower = title.lower()
        content_lower = content.lower() if content else ""
        
        if study_lower in title_lower or study_lower in content_lower:
            return {
                "decision": "ALLOW",
                "reason": f"Content mentions '{study_goal}'",
                "confidence": 0.8
            }
        
        return {
            "decision": "BLOCK",
            "reason": f"Content appears unrelated to '{study_goal}'",
            "confidence": 0.6
        }


# Create a global instance
llm = LLMClassifier()