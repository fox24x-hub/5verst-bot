# services/knowledge.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FIVE_VERST_FILE = DATA_DIR / "5-verst.txt"
POSTS_STRUCTURED_FILE = DATA_DIR / "posts_examples_structured.md"
POSTS_EXAMPLES_FILE = DATA_DIR / "posts_examples.md"


def _safe_read(path: Path) -> str:
    """Безопасно читает файл, если он существует."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_five_verst_knowledge() -> str:
    """
    Загружает полный текст о движении «5 вёрст».
    Используется как фактическая база для постов, но не копируется дословно.
    """
    return _safe_read(FIVE_VERST_FILE)


def load_posts_structured_examples() -> str:
    """
    Загружает структурированные примеры постов (ПН, ПТ, СБ, ВС и т.д.).
    Удобно подмешивать как few-shot примеры в промпты.
    """
    return _safe_read(POSTS_STRUCTURED_FILE)


def load_posts_examples() -> str:
    """
    Загружает дополнительные примеры постов в свободной форме.
    """
    return _safe_read(POSTS_EXAMPLES_FILE)


# Загружаем сразу при импорте модуля, чтобы не читать файл каждый раз
FIVE_VERST_KNOWLEDGE = load_five_verst_knowledge()
POSTS_STRUCTURED_EXAMPLES = load_posts_structured_examples()
POSTS_EXAMPLES = load_posts_examples()
