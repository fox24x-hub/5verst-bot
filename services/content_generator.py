from services.prompts import FIVE_VERST_CONTENT_SYSTEM_PROMPT, POST_STRUCTURE  # POST_STRUCTURE можно вынести отдельно
from services.openai_client import client

async def generate_post(topic: str, location: str | None = None) -> str:
    location_part = f"Локация: {location}\n" if location else ""
    user_prompt = (
        f"Тема поста: {topic}\n"
        f"{location_part}\n"
        f"{POST_STRUCTURE}\n\n"
        "Соблюдай все требования к стилю, ограничения и формат ответа из system-промпта."
    )

    completion = await client.responses.create(
        model="gpt-4.0o-mini",
        input=[
            {"role": "system", "content": FIVE_VERST_CONTENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=800,
    )
    return completion.output[0].content[0].text

