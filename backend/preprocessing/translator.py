import asyncio
from groq import AsyncGroq
from backend.config import GROQ_API_KEY, GROQ_MODEL

client = AsyncGroq(api_key=GROQ_API_KEY)

async def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == 'en':
        return text
    prompt = f"Translate this text from {source_lang} to English. Return ONLY the translated English text, nothing else.\n\nText: {text}"
    try:
        response = await client.chat.completions.create(
            messages=[{'role': 'user', 'content': prompt}],
            model=GROQ_MODEL,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation Error: {e}")
        return text

async def translate_correction(correction: str, sources: list, target_lang: str) -> dict:
    if target_lang == 'en':
        return {'correction': correction, 'sources': sources}

    lang_name = {
        'hi': 'Hindi', 'ar': 'Arabic', 'es': 'Spanish', 'fr': 'French',
        'pt': 'Portuguese', 'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali',
        'sw': 'Swahili', 'ha': 'Hausa', 'yo': 'Yoruba', 'id': 'Indonesian',
        'kn': 'Kannada', 'ml': 'Malayalam', 'mr': 'Marathi', 'gu': 'Marathi'
    }.get(target_lang, target_lang)

    prompt = f"Translate this health fact-check correction to {lang_name} (easy to understand local dialect, simple words, like explaining to a 10-year-old). Keep all scientific terms accurate. Return ONLY the translated correction text.\n\nCorrection: {correction}"
    
    try:
        response = await client.chat.completions.create(
            messages=[{'role': 'user', 'content': prompt}],
            model=GROQ_MODEL,
            temperature=0.2,
        )
        return {'correction': response.choices[0].message.content.strip(), 'sources': sources}
    except Exception as e:
        print(f"Translation Error: {e}")
        return {'correction': correction, 'sources': sources}
