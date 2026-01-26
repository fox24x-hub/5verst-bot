import os
import json
from datetime import datetime

STATS_FILE = "data/users_stats.json"
os.makedirs("data", exist_ok=True)

# Admin ID
ADMIN_ID = 106041882

def load_stats():
    """Загрузить статистику использования"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_stats(stats: dict):
    """Сохранить статистику использования"""
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def track_user_action(user_id: int, action: str):
    """
    Отслеживать действие пользователя
    
    Args:
        user_id: ID пользователя Telegram
        action: Название действия (например: "generate_post", "ask_question", "add_example")
    """
    stats = load_stats()
    user_id_str = str(user_id)
    
    if user_id_str not in stats:
        stats[user_id_str] = {
            "user_id": user_id,
            "first_seen": datetime.now().isoformat(),
            "last_action": None,
            "actions": {},
            "total_actions": 0
        }
    
    # Обновляем статистику
    if "actions" not in stats[user_id_str]:
        stats[user_id_str]["actions"] = {}
    
    actions_dict = stats[user_id_str]["actions"]
    if action not in actions_dict:
        actions_dict[action] = 0
    
    actions_dict[action] += 1
    stats[user_id_str]["total_actions"] = stats[user_id_str].get("total_actions", 0) + 1
    stats[user_id_str]["last_action"] = datetime.now().isoformat()
    
    save_stats(stats)

def get_user_stats(user_id: int) -> dict:
    """Получить статистику конкретного пользователя"""
    stats = load_stats()
    user_id_str = str(user_id)
    return stats.get(user_id_str, {})

def get_all_stats() -> dict:
    """Получить полную статистику"""
    return load_stats()

def format_stats_report() -> str:
    """
    Форматировать отчет по статистике для администратора
    """
    stats = get_all_stats()
    
    if not stats:
        return "📊 **Статистика**\n\nДанных нет."
    
    # Сортируем пользователей по количеству действий
    sorted_users = sorted(
        stats.items(),
        key=lambda x: x[1].get("total_actions", 0),
        reverse=True
    )
    
    report = "📊 **СТАТИСТИКА ИСПОЛЬЗОВАНИЯ БОТА**\n\n"
    report += f"👥 Всего пользователей: {len(stats)}\n\n"
    
    total_actions = sum(user_data.get("total_actions", 0) for user_data in stats.values())
    report += f"📈 Всего действий: {total_actions}\n\n"
    
    report += "🔝 **ТОП 20 ПОЛЬЗОВАТЕЛЕЙ:**\n\n"
    
    for idx, (user_id_str, user_data) in enumerate(sorted_users[:20], 1):
        user_id = user_data.get("user_id", user_id_str)
        total = user_data.get("total_actions", 0)
        last_action = user_data.get("last_action", "Неизвестно")
        
        # Преобразуем ISO format в более читаемый
        try:
            dt = datetime.fromisoformat(last_action)
            last_action_str = dt.strftime("%d.%m %H:%M")
        except:
            last_action_str = "Неизвестно"
        
        actions_detail = user_data.get("actions", {})
        actions_str = ", ".join([
            f"{action}({count})"
            for action, count in sorted(actions_detail.items(), key=lambda x: x[1], reverse=True)[:3]
        ])
        
        report += f"{idx}. **ID: {user_id}** | Действий: {total}\n"
        report += f"   Последнее: {last_action_str}\n"
        report += f"   {actions_str}\n\n"
    
    # Статистика по типам действий
    action_totals = {}
    for user_data in stats.values():
        for action, count in user_data.get("actions", {}).items():
                action_totals[action] = action_totals.get(action, 0) + count    
    report += "\n📌 **ДЕЙСТВИЯ ПО ТИПАМ:**\n\n"
    for action, count in sorted(action_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_actions * 100) if total_actions > 0 else 0
        report += f"• {action}: {count} ({percentage:.1f}%)\n"
    
    return report
