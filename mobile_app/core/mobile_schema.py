# Path: mobile_app/core/mobile_schema.py
# Version: Kivy_1.0
# Description: Пути к файлам. Адаптировано для Kivy/Buildozer.

import os
import sys
import platform

def get_writable_root():
    # Проверка на Android (Kivy выставляет переменную окружения)
    if "ANDROID_ARGUMENT" in os.environ:
        # На Android пишем во внутреннюю память приложения
        # Обычно это /data/user/0/org.test.myapp/files/
        return os.path.expanduser("~")
    
    # На ПК (Windows/Linux) пишем в папку config рядом с кодом
    # Чтобы не засорять корень, поднимемся на уровень выше от core/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_dir

DATA_ROOT = get_writable_root()
CONFIG_DIR = os.path.join(DATA_ROOT, "config")

# Создаем папку, если нужно (и если есть права)
try:
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    print(f"[SYS LOG] Config dir checked at: {CONFIG_DIR}")
except Exception as e:
    print(f"[SYS LOG] Error creating config dir: {e}")

# Пути к файлам
FAS_PATH = os.path.join(CONFIG_DIR, "fas.json")
DB_PATH = os.path.join(CONFIG_DIR, "mobile_data.db")
DRAFT_PATH = os.path.join(CONFIG_DIR, "draft_state.json") # Новое: файл черновика

print(f"[SYS LOG] Paths initialized. DB: {DB_PATH}")