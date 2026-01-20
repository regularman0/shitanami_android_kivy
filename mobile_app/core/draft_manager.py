# Path: mobile_app/core/draft_manager.py
# Version: Kivy_1.0
# Description: Менеджер черновика. Использует локальный JSON файл для персистентности.

import json
import os
from datetime import datetime, timedelta
from core import mobile_schema

DT_FMT = "%d.%m.%Y %H:%M"

class DraftManager:
    def __init__(self):
        # Основные данные (Payload)
        self.data = {
            "range": {"or_range_val": "", "end_range_val": ""},
            "checkboxes": [],
            "tags": [],
            "category_path": []
        }
        
        # Состояние UI (счетчики)
        self.ui_state = {}
        
        # Загружаем состояние при старте
        self._load()

    def _save(self):
        """Сохраняет состояние в JSON файл"""
        try:
            full_state = {
                "data": self.data,
                "ui_state": self.ui_state
            }
            with open(mobile_schema.DRAFT_PATH, "w", encoding="utf-8") as f:
                json.dump(full_state, f, ensure_ascii=False, indent=2)
            print("[DATA LOG] Draft saved to disk")
        except Exception as e:
            print(f"[DATA LOG] Error saving draft: {e}")

    def _load(self):
        """Загружает состояние из JSON файла"""
        if not os.path.exists(mobile_schema.DRAFT_PATH):
            return
            
        try:
            with open(mobile_schema.DRAFT_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
                if stored:
                    self.data = stored.get("data", self.data)
                    self.ui_state = stored.get("ui_state", {})
            print("[DATA LOG] Draft loaded from disk")
        except Exception as e:
            print(f"[DATA LOG] Error loading draft: {e}")

    def clear(self):
        """Очистка после сохранения"""
        self.data["tags"] = []
        self.data["checkboxes"] = []
        self.data["range"]["or_range_val"] = ""
        self.data["range"]["end_range_val"] = ""
        
        # Сбрасываем счетчики UI
        self.ui_state = {}
        self._save()

    # --- UI STATE COUNTERS ---
    def get_ui_count(self, key, default=1):
        return self.ui_state.get(key, default)

    def set_ui_count(self, key, count):
        self.ui_state[key] = count
        self._save()

    # --- PATH ---
    def set_path(self, path):
        self.data["category_path"] = path
        self._save()
    
    def get_path(self):
        return self.data.get("category_path", [])

    # --- RANGE ---
    def get_range(self):
        return self.data["range"].get("or_range_val", ""), self.data["range"].get("end_range_val", "")

    def set_range(self, start, end):
        self.data["range"]["or_range_val"] = start or ""
        self.data["range"]["end_range_val"] = end or ""
        self._save()

    def set_manual_time(self, target, value_str):
        if not value_str:
            if target == "start": self.data["range"]["or_range_val"] = ""
            else: self.data["range"]["end_range_val"] = ""
            self._save()
            return True
        try:
            datetime.strptime(value_str, DT_FMT)
            if target == "start": self.data["range"]["or_range_val"] = value_str
            else: self.data["range"]["end_range_val"] = value_str
            self._save()
            return True
        except ValueError:
            return False

    def shift_range(self, minutes, op="add"):
        s, e = self.get_range()
        try:
            s_dt = datetime.strptime(s, DT_FMT)
            e_dt = datetime.strptime(e, DT_FMT)
        except: s_dt = e_dt = datetime.now()

        delta = timedelta(minutes=minutes)
        if op == "sub": delta = -delta
        
        new_s = (s_dt + delta).strftime(DT_FMT)
        new_e = (e_dt + delta).strftime(DT_FMT)
        self.set_range(new_s, new_e)
        return new_s, new_e

    def modify_one_bound(self, target="start", minutes=5, op="add"):
        s, e = self.get_range()
        try:
            dt_str = s if target == "start" else e
            if not dt_str: dt_str = datetime.now().strftime(DT_FMT)
            dt = datetime.strptime(dt_str, DT_FMT)
        except: dt = datetime.now()

        delta = timedelta(minutes=minutes)
        if op == "sub": delta = -delta
        new_dt = (dt + delta).strftime(DT_FMT)
        
        if target == "start": self.set_range(new_dt, e)
        else: self.set_range(s, new_dt)
        return new_dt

    def sync_duration(self, minutes):
        end = datetime.now()
        start = end - timedelta(minutes=minutes)
        s_str = start.strftime(DT_FMT)
        e_str = end.strftime(DT_FMT)
        self.set_range(s_str, e_str)
        return s_str, e_str

    # --- CHECKBOXES ---
    def toggle_checkbox(self, db_name, is_checked):
        self.data["checkboxes"] = [x for x in self.data["checkboxes"] if x["db_name"] != db_name]
        ts = ""
        if is_checked:
            ts = datetime.now().strftime(DT_FMT)
            self.data["checkboxes"].append({"db_name": db_name, "change_time": ts})
        self._save()
        return ts

    def get_checkbox_state(self, db_name):
        for x in self.data["checkboxes"]:
            if x["db_name"] == db_name: return True, x["change_time"]
        return False, ""

    # --- TAGS ---
    def update_tag(self, db_name, value):
        self.data["tags"] = [x for x in self.data["tags"] if x["db_name"] != db_name]
        if value:
            self.data["tags"].append({"db_name": db_name, "value": value})
        self._save()

    def get_tag_value(self, db_name):
        for x in self.data["tags"]:
            if x["db_name"] == db_name: return x["value"]
        return ""
    
    # --- EXPORT ---
    def export_for_save(self):
        flat = {}
        flat["category_path"] = "/".join(self.data.get("category_path", []))
        flat["range_start"] = self.data["range"].get("or_range_val", "")
        flat["range_end"] = self.data["range"].get("end_range_val", "")
        for t in self.data["tags"]: flat[f"T_{t['db_name'].upper()}"] = t["value"]
        for c in self.data["checkboxes"]: flat[f"C_{c['db_name'].upper()}"] = c["change_time"]
        return flat

# Глобальный экземпляр
draft = DraftManager()