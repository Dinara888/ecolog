import logging
import sys
from datetime import datetime
from pathlib import Path

# Гарантируем импорт из соседних модулей пакета src
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import load_config
from db import init_db, save_entry, load_entries
from analytics import (calculate_eco_score, get_weekly_scores,
                       render_progress, generate_insights)
from data_manager import export_to_zip, import_from_zip

def setup_logging(log_path: Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def input_date() -> str:
    while True:
        try:
            d = input("Дата (YYYY-MM-DD) или ENTER для сегодня: ").strip()
            d = d if d else datetime.now().strftime("%Y-%m-%d")
            datetime.strptime(d, "%Y-%m-%d")
            return d
        except ValueError:
            print("❌ Неверный формат даты.")

def input_int(prompt: str, low: int, high: int) -> int:
    while True:
        try:
            val = int(input(f"{prompt} ({low}-{5}): "))
            if low <= val <= high:
                return val
            print(f"❌ Число от {low} до {high}.")
        except ValueError:
            print("❌ Введите целое число.")

def add_entry(cfg: dict) -> None:
    date = input_date()
    print("🌿 Действия (номера через запятую):")
    print("1) Использовал многоразовую бутылку")
    print("2) Отказался от пластика")
    print("3) Сдал вторсырьё")
    print("4) Проехал на велосипеде/общественном транспорте")
    print("5) Потушил свет при выходе")
    raw = input("Выбор: ")
    actions_map = {
        "1": "Использовал многоразовую бутылку",
        "2": "Отказался от пластика",
        "3": "Сдал вторсырьё",
        "4": "Проехал на велосипеде/общественном транспорте",
        "5": "Потушил свет при выходе"
    }
    actions = [
        actions_map[x.strip()] for x in raw.split(",")
        if x.strip() in actions_map
    ]
    if not actions:
        print("⚠️ Действия не выбраны.")
        return

    waste = input_int("Мусор (1=мало, 5=много)", 1, 5)
    water = input_int("Вода (1=экономно, 5=много)", 1, 5)
    elec = input_int("Электричество (1=экономно, 5=много)", 1, 5)
    notes = input("Заметки (опционально): ").strip()

    entry = {
        "date": date, "actions": actions, "waste_level": waste,
        "water_usage": water, "electricity_usage": elec, "notes": notes
    }
    save_entry(cfg["db_path"], entry)
    print("✅ Запись сохранена!")

def show_analytics(cfg: dict) -> None:
    entries = load_entries(cfg["db_path"])
    if not entries:
        print("📭 Нет записей.")
        return

    weeks = get_weekly_scores(entries)
    print("\n📊 Эко-прогресс:")
    print(render_progress(weeks))
    print("\n💡 Инсайты:")
    for i in generate_insights(entries):
        print(f"  • {i}")

    if len(entries) > 1:
        prev = calculate_eco_score(entries[:1])
        curr = calculate_eco_score(entries)
        if curr > prev:
            print("🎉 Отлично! Вы побили свой рекорд!")

def export_data(cfg: dict) -> None:
    entries = load_entries(cfg["db_path"])
    zip_path = Path("ecolog_backup.zip")
    export_to_zip(entries, cfg["db_path"], zip_path, cfg["backup_dir"])
    print(f"📦 Экспорт в {zip_path}")

def import_data(cfg: dict) -> None:
    path = input("Путь к ZIP: ").strip()
    try:
        import_from_zip(Path(path), cfg["db_path"])
        print("✅ Импорт завершён.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logging.error(f"Import failed: {e}")

def menu(cfg: dict) -> None:
    while True:
        print("\n🌍 EcoLog Меню:")
        print("1) Добавить запись")
        print("2) Аналитика")
        print("3) Экспорт")
        print("4) Импорт")
        print("5) Выход")
        try:
            choice = input("Выбор: ").strip()
            if choice == "1": add_entry(cfg)
            elif choice == "2": show_analytics(cfg)
            elif choice == "3": export_data(cfg)
            elif choice == "4": import_data(cfg)
            elif choice == "5": break
            else: print("❌ Неверный пункт.")
        except KeyboardInterrupt:
            print("\n👋 Завершение...")
            break
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            logging.error(f"Menu error: {e}")

if __name__ == "__main__":
    cfg = load_config()
    setup_logging(cfg["log_file"])
    init_db(cfg["db_path"])
    menu(cfg)