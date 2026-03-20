import base64
import json
from groq import AsyncGroq
from backend.config import GROQ_API_KEY

async def extract_text_from_image(image_bytes: bytes) -> str:
    client = AsyncGroq(api_key=GROQ_API_KEY)
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    try:
        response = await client.chat.completions.create(
            model='llama-3.2-11b-vision-preview',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': 'Extract all text from this image. Specifically look for health claims, medical advice, or meme text.'},
                        {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}}
                    ]
                }
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f'Vision API Error: {e}')
        return ''
