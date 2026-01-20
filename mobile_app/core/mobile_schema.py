# Path: mobile_app/core/mobile_schema.py
# Version: Kivy_1.2
# Description: Пути к файлам. Исправлено добавление DRAFT_PATH.

import os
import sys
from kivy.utils import platform

def get_writable_root():
    # 1. Android
    if platform == 'android':
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        return activity.getFilesDir().getAbsolutePath()
    
    # 2. ПК (Windows/Linux)
    current_file = os.path.abspath(__file__)
    core_dir = os.path.dirname(current_file)
    app_dir = os.path.dirname(core_dir)
    root_dir = os.path.dirname(app_dir)
    return root_dir

DATA_ROOT = get_writable_root()
CONFIG_DIR = os.path.join(DATA_ROOT, "config")

if not os.path.exists(CONFIG_DIR):
    try:
        os.makedirs(CONFIG_DIR)
    except OSError:
        pass

FAS_PATH = os.path.join(CONFIG_DIR, "fas.json")
DB_PATH = os.path.join(CONFIG_DIR, "mobile_data.db")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "app_settings.json")
DRAFT_PATH = os.path.join(CONFIG_DIR, "draft_state.json") # <--- ДОБАВЛЕНО

print(f"[SYS LOG] Paths initialized. Config dir: {CONFIG_DIR}")