from services.prompts import FIVE_VERST_CONTENT_SYSTEM_PROMPT, POST_STRUCTURE
from services.knowledge import (
    FIVE_VERST_KNOWLEDGE,
    POSTS_STRUCTURED_EXAMPLES,
)
from services.openai_client import client


async def generate_post(topic: str, location: str | None = None) -> str:
    """
    Генерирует пост для мовения «5 вёрст» на заданную тему.
    
    Args:
        topic: Тема поста (напр., 'первый старт', 'теплые встречи')
        location: Локация/город (напр., 'Екатеринбург')
    
    Returns:
        Готовый текст поста в заданной структуре.
    """
    location_part = f"\nЛокация: {location}" if location else ""
    
    user_prompt = (
        f"""
Основная информация о движении «5 вёрст»:
{FIVE_VERST_KNOWLEDGE[:3000]}

Примеры постов на похожие темы (на них ориентируйся по тону и структуре):
{POSTS_STRUCTURED_EXAMPLES[:2000]}

{POST_STRUCTURE}

Тема: {topic}{location_part}

Основное требование: напиши пост в дружелюбном стиле без спортивного фетиша, с акцентом на волонтёрах и людях.
"""
    )
    
    completion = await client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": FIVE_VERST_CONTENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=800,
    )
    
    return completion.output[0].content[0].text
