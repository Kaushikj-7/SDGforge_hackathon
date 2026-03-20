import pathlib


def clean(path_str):
    p = pathlib.Path(path_str)
    try:
        txt = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        txt = p.read_text(encoding="latin1")

    # Common windows power shell manglings
    txt = txt.replace('â€"', "-")
    txt = txt.replace("â€”", "-")
    txt = txt.replace("Ã—", "x")
    txt = txt.replace("Â±", "+-")
    txt = txt.replace("âœ“", "Check ")
    txt = txt.replace("✓", "Check ")

    p.write_text(txt, encoding="utf-8")


clean("browser-extension/content.js")
clean("browser-extension/popup.html")
clean("extension/content.js")
clean("extension/popup.html")

print("cleanup done")
