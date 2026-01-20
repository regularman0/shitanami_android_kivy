# Path: mobile_app/core/database.py
# Version: 2.0
# Description: Локальная БД. Исправлен путь (берется из mobile_schema для совместимости с Android).

import sqlite3
import uuid
from datetime import datetime
# ИСПРАВЛЕНИЕ: Импортируем путь из схемы, где прописана логика для Android
from .mobile_schema import DB_PATH

class Database:
    def __init__(self):
        self.conn = None
        # Инициализация происходит при импорте. 
        # На Android важно, чтобы путь DB_PATH уже был корректным (writable).
        self.init_db()

    def connect(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()

    def init_db(self):
        cur = self.connect()
        # Таблица событий
        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            timestamp TEXT,
            updated_at TEXT,
            is_deleted INTEGER DEFAULT 0,
            category_path TEXT,
            range_start TEXT,
            range_end TEXT,
            synced INTEGER DEFAULT 0 
        )
        """)
        # Таблица мета-данных
        cur.execute("""
        CREATE TABLE IF NOT EXISTS app_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        self.conn.commit()

    # --- META ---
    def get_last_sync_time(self):
        cur = self.conn.execute("SELECT value FROM app_meta WHERE key='last_sync'")
        res = cur.fetchone()
        return res["value"] if res else None

    def set_last_sync_time(self, iso_time):
        self.conn.execute("INSERT OR REPLACE INTO app_meta (key, value) VALUES ('last_sync', ?)", (iso_time,))
        self.conn.commit()

    # --- RECORDS ---
    def add_record(self, data):
        new_id = str(uuid.uuid4())
        now_iso = datetime.now().isoformat()
        ts = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        base = {"id": new_id, "session_id": "MOBILE", "timestamp": ts, "updated_at": now_iso, "synced": 0, "is_deleted": 0}
        full_data = {**base, **data}
        return self.upsert_record(full_data)

    def upsert_record(self, data):
        self._ensure_columns(list(data.keys()))
        cols = ",".join(data.keys())
        placeholders = ",".join(["?"] * len(data))
        vals = list(data.values())
        query = f"INSERT OR REPLACE INTO events ({cols}) VALUES ({placeholders})"
        try:
            self.conn.execute(query, vals)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Upsert error: {e}")
            return False

    def get_unsynced(self):
        cur = self.conn.execute("SELECT * FROM events WHERE synced = 0")
        return [dict(row) for row in cur.fetchall()]

    def mark_as_synced(self, id_list):
        if not id_list: return
        p = ",".join(f"'{x}'" for x in id_list)
        self.conn.execute(f"UPDATE events SET synced = 1 WHERE id IN ({p})")
        self.conn.commit()
        
    def get_last_range_end(self):
        """Возвращает время окончания последней НЕ удаленной записи"""
        try:
            cur = self.conn.execute("SELECT range_end FROM events WHERE is_deleted = 0 ORDER BY updated_at DESC LIMIT 1")
            row = cur.fetchone()
            if row and row["range_end"]:
                return row["range_end"]
            return None
        except: return None

    def _ensure_columns(self, keys):
        cur = self.conn.execute("PRAGMA table_info(events)")
        existing = [r["name"] for r in cur.fetchall()]
        for k in keys:
            if k not in existing:
                try: self.conn.execute(f"ALTER TABLE events ADD COLUMN {k} TEXT")
                except: pass

db = Database()