# make_presentation.py
import os, aiohttp, asyncio
from dotenv import load_dotenv

load_dotenv()
PRESENTON_API_KEY = os.getenv("PRESENTON_API_KEY")

# 👉 облачный API
API_URL = "https://api.presenton.ai/api/v1/ppt/presentation/generate"

async def generate_presentation(content: str, n_slides: int = 8, language: str = "Russian") -> dict:
    """
    Отправляет транскрипт/резюме в Presenton API и возвращает данные о презентации.
    """
    if not PRESENTON_API_KEY:
        raise RuntimeError("❌ Не найден PRESENTON_API_KEY в .env")

    headers = {
        "Authorization": f"Bearer {PRESENTON_API_KEY}",
        "Content-Type": "application/json",
    }

    # 🔥 Промпт для красивой презентации
    instructions = (
        f"Создай красивую презентацию на {language} языке "
        "с чётким планом, минимум текста на слайдах, "
        "оформлением с красивыми градиентными фонами и картинками. "
        "Используй структуру: введение, основные пункты, вывод. "
        "Добавь красивые background, а не просто белый фон."
        "Добавь различные красивые символы."
    )

    payload = {
        "content": content,
        "n_slides": n_slides,
        "language": language,
        "template": "general",
        "export_as": "pptx",
        "instructions": instructions,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json=payload) as resp:
            if resp.status >= 400:
                body = await resp.text()
                raise RuntimeError(f"Presenton {resp.status}: {body}")
            return await resp.json()


# Для локального теста
if __name__ == "__main__":
    async def test():
        text = "Тестовый транскрипт.\nРезюме: проверка генерации презентации."
        result = await generate_presentation(text, n_slides=5, language="Russian")
        print(result)

    asyncio.run(test())
