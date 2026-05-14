import os
from pathlib import Path
from dotenv import load_dotenv

def load_config() -> dict:
    load_dotenv()
    return {
        "db_path": Path(os.getenv("DB_PATH", "ecolog.sqlite")),
        "log_file": Path(os.getenv("LOG_FILE", "app.log")),
        "backup_dir": Path(os.getenv("BACKUP_DIR", "backups"))
    }