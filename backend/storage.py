import os
import threading
from pathlib import Path
from typing import Optional

from tinydb import TinyDB

DEFAULT_DB_PATH = "backend/data/items.json"


class Storage:
    def __init__(self, db_path: Optional[str] = None) -> None:
        path = Path(db_path or os.environ.get("DB_PATH", DEFAULT_DB_PATH))
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = TinyDB(str(path))
        self._lock = threading.Lock()

    def insert(self, item: dict) -> None:
        with self._lock:
            self._db.insert(item)

    def list_all(self) -> list[dict]:
        with self._lock:
            items = [dict(doc) for doc in self._db.all()]
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items

    def close(self) -> None:
        with self._lock:
            self._db.close()
