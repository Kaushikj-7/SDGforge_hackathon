# API Configuration Template for Health Misinformation Detection System
# Copy this file to config.py and add your actual API keys

# Groq API (Fast LLM inference - recommended for medical analysis)
# Get your free API key at: https://console.groq.com/
GROQ_API_KEY = "your_groq_api_key_here"

# Gemini API (Google's AI with strong medical knowledge)
# Get your free API key at: https://ai.google.dev/
GEMINI_API_KEY = "your_gemini_api_key_here"

# Optional: OpenAI API (if you want to compare)
OPENAI_API_KEY = ""

# Optional: Hugging Face API (for BioBERT - not needed with Groq/Gemini)
HUGGINGFACE_API_KEY = ""

# API Endpoints
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Model configurations
GROQ_MODEL = "llama3-70b-8192"  # Best for medical reasoning
GEMINI_MODEL = "gemini-1.5-flash"  # Faster, less quota usage (fallback: gemini-1.5-pro)
