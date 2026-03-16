with open("backend/config.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('GROQ_API_KEY    = os.getenv("GROQ_API_KEY")', 'GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "dummy_groq_key")')
c = c.replace('GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")', 'GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "dummy_gemini_key")')

with open("backend/config.py", "w", encoding="utf-8") as f:
    f.write(c)
