import os
import asyncio
import hashlib

from typing import List, Dict
from openai import AsyncOpenAI
from services.cache_service import get_cache, set_cache



client = AsyncOpenAI(api_key=os.getenv("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"))



def generate_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()



async def _safe_request(messages: List[Dict[str, str]]) -> str:
    for _ in range(3):
        try:

            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages
                ),
                timeout=10
            )
            return response.choices[0].message.content or ""

        except Exception:
            await asyncio.sleep(1)

    return "AI cevap veremedi."



async def ai_analysis(summary: str) -> str:
    key = generate_key(summary)


    cached = get_cache(key)
    if cached:
        print("⚡ CACHE HIT")
        return cached


    result = await _safe_request([
        {"role": "system", "content": "Veriyi analiz et"},
        {"role": "user", "content": summary}
    ])


    set_cache(key, result, expire=3600)


    return result