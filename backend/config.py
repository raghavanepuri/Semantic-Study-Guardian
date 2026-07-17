"""
Configuration settings for the backend.
This keeps hardcoded values in one place instead of scattered throughout the code.
"""

# LLM Configuration
OLLAMA_BASE_URL = "http://localhost:11434"  # Change this when moving to college server
OLLAMA_MODEL = "qwen2:4b"  # Model name (we'll use this later)

# API Configuration
API_PORT = 8000
API_HOST = "127.0.0.1"

# Inference Configuration
MAX_TOKENS = 100
TEMPERATURE = 0.3  # Lower = more consistent, Higher = more creative