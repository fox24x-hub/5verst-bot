import json
import os
from datetime import datetime

STATS_FILE = "data/users_stats.json"
os.makedirs("data", exist_ok=True)


def _get_admin_id() -> int:
    value = os.getenv("ADMIN_ID", "106041882")
    try:
        return int(value)
    except ValueError:
        return 106041882


ADMIN_ID = _get_admin_id()


def load_stats() -> dict:
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_stats(stats: dict) -> None:
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def track_user_action(user_id: int, action: str) -> None:
    stats = load_stats()
    user_id_str = str(user_id)

    if user_id_str not in stats:
        stats[user_id_str] = {
            "user_id": user_id,
            "first_seen": datetime.now().isoformat(),
            "last_action": None,
            "actions": {},
            "total_actions": 0,
        }

    actions_dict = stats[user_id_str].setdefault("actions", {})
    actions_dict[action] = actions_dict.get(action, 0) + 1
    stats[user_id_str]["total_actions"] = stats[user_id_str].get("total_actions", 0) + 1
    stats[user_id_str]["last_action"] = datetime.now().isoformat()

    save_stats(stats)


def get_user_stats(user_id: int) -> dict:
    stats = load_stats()
    return stats.get(str(user_id), {})


def get_all_stats() -> dict:
    return load_stats()


def format_stats_report() -> str:
    stats = get_all_stats()
    if not stats:
        return "📊 **Статистика**\n\nДанных нет."

    sorted_users = sorted(
        stats.items(),
        key=lambda item: item[1].get("total_actions", 0),
        reverse=True,
    )

    total_actions = sum(user_data.get("total_actions", 0) for user_data in stats.values())

    report = "📊 **СТАТИСТИКА ИСПОЛЬЗОВАНИЯ БОТА**\n\n"
    report += f"👥 Всего пользователей: {len(stats)}\n\n"
    report += f"⚡ Всего действий: {total_actions}\n\n"
    report += "🏆 **ТОП 20 ПОЛЬЗОВАТЕЛЕЙ:**\n\n"

    for idx, (user_id_str, user_data) in enumerate(sorted_users[:20], 1):
        user_id = user_data.get("user_id", user_id_str)
        total = user_data.get("total_actions", 0)
        last_action = user_data.get("last_action", "Неизвестно")

        try:
            dt = datetime.fromisoformat(last_action)
            last_action_str = dt.strftime("%d.%m %H:%M")
        except ValueError:
            last_action_str = "Неизвестно"

        actions_detail = user_data.get("actions", {})
        top_actions = sorted(actions_detail.items(), key=lambda item: item[1], reverse=True)[:3]
        actions_str = ", ".join(f"{action}({count})" for action, count in top_actions)

        report += f"{idx}. **ID: {user_id}** | Действий: {total}\n"
        report += f"   Последнее: {last_action_str}\n"
        report += f"   {actions_str}\n\n"

    action_totals: dict[str, int] = {}
    for user_data in stats.values():
        for action, count in user_data.get("actions", {}).items():
            action_totals[action] = action_totals.get(action, 0) + count

    report += "\n📈 **ДЕЙСТВИЯ ПО ТИПАМ:**\n\n"
    for action, count in sorted(action_totals.items(), key=lambda item: item[1], reverse=True):
        percentage = (count / total_actions * 100) if total_actions > 0 else 0
        report += f"- {action}: {count} ({percentage:.1f}%)\n"

    return report
