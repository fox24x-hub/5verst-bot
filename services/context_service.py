import json
import os

CONTEXT_FILE = "data/user_contexts.json"
os.makedirs("data", exist_ok=True)


def _load_contexts() -> dict:
    if os.path.exists(CONTEXT_FILE):
        try:
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_contexts(contexts: dict) -> None:
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(contexts, f, ensure_ascii=False, indent=2)


def set_last_generated_post(user_id: int, post_text: str) -> None:
    contexts = _load_contexts()
    user_key = str(user_id)
    user_ctx = contexts.get(user_key, {})
    user_ctx["last_generated_post"] = post_text
    contexts[user_key] = user_ctx
    _save_contexts(contexts)


def get_last_generated_post(user_id: int) -> str | None:
    contexts = _load_contexts()
    user_ctx = contexts.get(str(user_id), {})
    value = user_ctx.get("last_generated_post")
    if isinstance(value, str) and value.strip():
        return value
    return None
