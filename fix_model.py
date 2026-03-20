import os

with open("backend/agent/orchestrator.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("llama3-70b-8192", "llama-3.3-70b-versatile")

with open("backend/agent/orchestrator.py", "w", encoding="utf-8") as f:
    f.write(text)
    
with open("backend/config.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("llama3-70b-8192", "llama-3.3-70b-versatile")

with open("backend/config.py", "w", encoding="utf-8") as f:
    f.write(text)
    
with open("backend/phases/phase4_misinformation_detection.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("llama3-70b-8192", "llama-3.3-70b-versatile")

with open("backend/phases/phase4_misinformation_detection.py", "w", encoding="utf-8") as f:
    f.write(text)
