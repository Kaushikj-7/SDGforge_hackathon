import langdetect

LANG_MAP = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 
    'zh-cn': 'Chinese', 'hi': 'Hindi', 'ar': 'Arabic', 'pt': 'Portuguese',
    'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean', 'it': 'Italian',
    'bn': 'Bengali', 'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu'
}

def detect_language(text: str) -> dict:
    try:
        code = langdetect.detect(text)
        name = LANG_MAP.get(code, code.upper())
        return {'code': code, 'name': name, 'supported': True}
    except Exception:
        return {'code': 'en', 'name': 'English', 'supported': True}
