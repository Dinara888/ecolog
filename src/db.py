import sqlite3
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def init_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS eco_entries (
                date TEXT PRIMARY KEY,
                actions_json TEXT NOT NULL,
                waste_level INTEGER,
                water_usage INTEGER,
                electricity_usage INTEGER,
                notes TEXT
            )
        """)
        conn.commit()
    logger.info("База данных инициализирована.")

def save_entry(db_path: Path, entry: dict) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO eco_entries
            (date, actions_json, waste_level, water_usage,
             electricity_usage, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry["date"],
            json.dumps(entry["actions"], ensure_ascii=False),
            entry["waste_level"],
            entry["water_usage"],
            entry["electricity_usage"],
            entry.get("notes", "")
        ))
        conn.commit()
    logger.info(f"Запись за {entry['date']} сохранена.")

def load_entries(db_path: Path, days: int = None) -> list:
    from datetime import datetime, timedelta
    query = "SELECT * FROM eco_entries ORDER BY date DESC"
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        query += f" WHERE date >= '{cutoff}'"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
    return [
        {
            "date": r[0],
            "actions": json.loads(r[1]),
            "waste_level": r[2],
            "water_usage": r[3],
            "electricity_usage": r[4],
            "notes": r[5]
        } for r in rows
    ]