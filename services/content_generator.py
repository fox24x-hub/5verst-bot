from services.prompts import FIVE_VERST_CONTENT_SYSTEM_PROMPT
from services.openai_client import client

async def generate_post(topic: str) -> str:
    completion = await client.responses.create(
        model="gpt-4.0o-mini",
        input=[
            {"role": "system", "content": FIVE_VERST_CONTENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Создай пост на тему: {topic}"},
        ],
        max_output_tokens=800,
    )
    return completion.output[0].content[0].text
