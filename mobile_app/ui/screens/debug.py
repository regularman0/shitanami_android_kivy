# Path: mobile_app/ui/screens/debug.py
# Version: Kivy_1.0
# Description: Экран отладки. Показывает состояние черновика и локальной БД.

import json
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from core.draft_manager import draft
from core.database import db
from .base_screen import BaseScreen

class DebugScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "debug"
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(layout)
        
        # Заголовок + Кнопка обновления
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        lbl = Label(text="DEBUG INFO", color=(0,0,0,1), bold=True, size_hint_x=0.7, halign='left')
        lbl.bind(size=lbl.setter('text_size'))
        
        btn_refresh = Button(text="🔄 Обновить", size_hint_x=0.3, background_color=(0.2, 0.6, 0.8, 1))
        btn_refresh.bind(on_release=self.refresh_data)
        
        top_bar.add_widget(lbl)
        top_bar.add_widget(btn_refresh)
        layout.add_widget(top_bar)
        
        # Поле вывода (ReadOnly)
        self.ti_log = TextInput(text="Нажми обновить...", readonly=True, font_family="Roboto", font_size='11sp')
        layout.add_widget(self.ti_log)
        
        # Автообновление при входе
        self.bind(on_enter=self.refresh_data)

    def refresh_data(self, *args):
        # 1. Draft Data
        debug_info = "=== DRAFT STATE (MEMORY) ===\n"
        debug_info += json.dumps(draft.data, indent=2, ensure_ascii=False)
        
        debug_info += "\n\n=== UI STATE (COUNTERS) ===\n"
        debug_info += json.dumps(draft.ui_state, indent=2, ensure_ascii=False)
        
        # 2. Local DB Data
        debug_info += "\n\n=== LOCAL DB (LAST 3) ===\n"
        try:
            # Прямой запрос для отладки
            cur = db.conn.execute("SELECT * FROM events ORDER BY updated_at DESC LIMIT 3")
            rows = [dict(r) for r in cur.fetchall()]
            debug_info += json.dumps(rows, indent=2, ensure_ascii=False)
        except Exception as e:
            debug_info += f"DB Error: {e}"
            
        self.ti_log.text = debug_info