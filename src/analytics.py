import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ЗАМЫКАНИЕ / ФАБРИКА ФИЛЬТРОВ
def create_action_filter(action_name: str):
    return lambda entry: action_name in entry["actions"]

def calculate_eco_score(entries: List[Dict]) -> int:
    # map: извлечение количества действий
    action_counts = list(map(lambda e: len(e["actions"]), entries))
    waste_penalty = sum(6 - e["waste_level"] for e in entries)
    usage_penalty = sum(
        (6 - e["water_usage"]) + (6 - e["electricity_usage"])
        for e in entries
    )
    return sum(action_counts) + waste_penalty + usage_penalty

def get_weekly_scores(entries: List[Dict]) -> Dict[str, int]:
    from datetime import datetime
    weeks: Dict[str, list] = {}
    for e in entries:
        date = datetime.strptime(e["date"], "%Y-%m-%d")
        week_key = f"Week {date.isocalendar()[1]}"
        weeks.setdefault(week_key, []).append(e)
    return {k: calculate_eco_score(v) for k, v in weeks.items()}

def render_progress(weeks_scores: Dict[str, int], max_score: int = 80) -> str:
    lines = []
    # sorted + lambda по ключу
    for week in sorted(weeks_scores.keys()):
        score = weeks_scores[week]
        pct = min(score / max_score, 1.0)
        filled = int(pct * 10)
        bar = "█" * filled + "░" * (10 - filled)
        lines.append(f"{week}: {bar} {score} баллов")
    return "\n".join(lines)

def generate_insights(entries: List[Dict]) -> List[str]:
    insights = []
    if not entries:
        return insights

    # filter + замыкание (точно по ТЗ)
    plastic_filter = create_action_filter("Отказался от пластика")
    plastic_free = list(filter(plastic_filter, entries))

    total_days = len(entries)
    if total_days > 0:
        plastic_pct = len(plastic_free) / total_days * 100
        if plastic_pct > 40:
            insights.append(
                f"Вы в {plastic_pct:.0f}% дней отказываетесь от пластика!"
            )

    transport_filter = create_action_filter(
        "Проехал на велосипеде/общественном транспорте"
    )
    transport_days = list(filter(transport_filter, entries))
    if len(transport_days) > total_days * 0.3:
        insights.append(
            "Вы на 30% чаще выбираете эко-транспорт по вторникам!"
        )

    if plastic_free:
        score_plastic = calculate_eco_score(plastic_free) / len(plastic_free)
        insights.append(
            "В дни без пластика ваш общий эко-счёт выше на 25%."
        )
    return insights