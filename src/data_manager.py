import csv
import json
import zipfile
import shutil
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def export_to_zip(entries: list, db_path: Path,
                  zip_path: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{ts}.sqlite"
    shutil.copy2(db_path, backup_dir / backup_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # CSV
        csv_lines = ["date,actions_count,waste_level\n"]
        for e in entries:
            csv_lines.append(
                f"{e['date']},{len(e['actions'])},{e['waste_level']}\n"
            )
        zf.writestr("ecolog_export.csv", "".join(csv_lines))

        # JSON
        zf.writestr(
            "ecolog_export.json",
            json.dumps(entries, ensure_ascii=False, indent=2)
        )
        # DB Backup
        zf.write(backup_dir / backup_name, arcname=backup_name)
    logger.info(f"Архив экспорта создан: {zip_path}")

def import_from_zip(zip_path: Path, db_path: Path) -> None:
    extract_dir = Path("temp_import")
    extract_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    db_files = list(extract_dir.glob("*.sqlite"))
    if not db_files:
        raise FileNotFoundError("В архиве не найдена копия БД.")

    shutil.copy2(db_files[0], db_path)
    shutil.rmtree(extract_dir)
    logger.info("База данных восстановлена из архива.")