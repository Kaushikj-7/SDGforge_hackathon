with open("backend/agent/tools.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("\\\"\\\"\\\"", "\"\"\"")
c = c.replace("\\\"", "\"")
with open("backend/agent/tools.py", "w", encoding="utf-8") as f:
    f.write(c)
