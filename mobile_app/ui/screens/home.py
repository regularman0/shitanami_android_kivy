# Path: mobile_app/ui/screens/home.py
# Version: Kivy_1.2
# Description: Экран ввода. Подключен TimeGenerator.

import json
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle

from .base_screen import BaseScreen
from core import mobile_schema
from core.draft_manager import draft
from core import config_utils
# ИМПОРТ ГЕНЕРАТОРА
from ui.generators.time_gen import TimeGenerator

class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        self.fas_data = {}
        
        # Инициализация
        self.time_gen = TimeGenerator(theme=None, fas_config=self.fas_data)
        
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.layout)

        # 1. Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        
        self.btn_back = Button(text="<", size_hint_x=None, width='40dp', background_color=(0.8, 0.3, 0.3, 1))
        self.btn_back.bind(on_release=self.go_back)
        
        lbl_title = Label(text="Новая запись", font_size='20sp', color=(0,0,0,1), bold=True)
        
        btn_clear = Button(text="X", size_hint_x=None, width='40dp', background_color=(0.8, 0.3, 0.3, 1))
        btn_clear.bind(on_release=self.clear_form)
        
        header.add_widget(self.btn_back)
        header.add_widget(lbl_title)
        header.add_widget(btn_clear)
        self.layout.add_widget(header)

        # 2. Nav
        self.nav_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.nav_container.bind(minimum_height=self.nav_container.setter('height'))
        self.layout.add_widget(self.nav_container)
        
        self.layout.add_widget(self._create_divider())
        
        # 3. Mode Switcher
        row_mode = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp')
        row_mode.add_widget(Label(text="Duration Mode (Shift):", color=(0,0,0,1), halign='right'))
        self.cb_mode = CheckBox(color=(0,0,0,1), size_hint_x=None, width='40dp')
        self.cb_mode.bind(active=self.on_mode_change)
        row_mode.add_widget(self.cb_mode)
        
        self.layout.add_widget(row_mode)

        # 4. Scroll Content
        self.scroll = ScrollView(size_hint=(1, 1))
        self.content_container = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=5)
        self.content_container.bind(minimum_height=self.content_container.setter('height'))
        self.scroll.add_widget(self.content_container)
        self.layout.add_widget(self.scroll)

        # 5. Save
        self.btn_save = Button(text="СОХРАНИТЬ", size_hint_y=None, height='50dp', background_color=(0.2, 0.7, 0.3, 1))
        self.btn_save.bind(on_release=self.save_record)
        self.layout.add_widget(self.btn_save)

        self.bind(on_enter=self.on_screen_enter)

    def _create_divider(self):
        d = BoxLayout(size_hint_y=None, height='2dp')
        with d.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(pos=d.pos, size=d.size)
        return d

    def on_screen_enter(self, *args):
        self.load_config()
        self.render_navigation()

    def load_config(self):
        if os.path.exists(mobile_schema.FAS_PATH):
            try:
                with open(mobile_schema.FAS_PATH, "r", encoding="utf-8") as f:
                    self.fas_data = json.load(f)
                # Update config in generator
                self.time_gen.fas_config = self.fas_data
            except Exception as e:
                Logger.error(f"[UI] Error loading FAS: {e}")
                
    def on_mode_change(self, instance, value):
        if self.time_gen:
            self.time_gen.set_mode(value)

    def render_navigation(self):
        self.nav_container.clear_widgets()
        current_path = draft.get_path()
        cursor = self.fas_data.get("category", {}).get("main", {}).get("children", {})
        
        for i, step in enumerate(current_path):
            options = list(cursor.keys())
            spinner = Spinner(text=step, values=options, size_hint_y=None, height='44dp',
                              background_normal='', background_color=(0.3, 0.5, 0.7, 1), color=(1, 1, 1, 1))
            spinner.bind(text=lambda instance, val, idx=i: self.on_spinner_select(idx, val))
            self.nav_container.add_widget(spinner)
            if step in cursor: cursor = cursor[step].get("children", {})
            else: cursor = {}; break

        if cursor:
            options = list(cursor.keys())
            if options:
                spinner = Spinner(text="Выберите...", values=options, size_hint_y=None, height='44dp',
                                  background_normal='', background_color=(0.8, 0.8, 0.8, 1), color=(0.2, 0.2, 0.2, 1))
                spinner.bind(text=lambda instance, val, idx=len(current_path): self.on_spinner_select(idx, val))
                self.nav_container.add_widget(spinner)

        self.render_dynamic_content(current_path)

    def on_spinner_select(self, index, value):
        current_path = draft.get_path()
        current_path = current_path[:index]
        current_path.append(value)
        draft.set_path(current_path)
        Clock.schedule_once(lambda dt: self.render_navigation())

    def go_back(self, *args):
        current_path = draft.get_path()
        if current_path:
            current_path.pop()
            draft.set_path(current_path)
            self.render_navigation()

    def clear_form(self, *args):
        draft.clear()
        self.render_navigation()

    def render_dynamic_content(self, path):
        self.content_container.clear_widgets()
        if not path: return

        ui_conf = config_utils.resolve_config(self.fas_data, path)
        active = ui_conf.get("active_modules", [])
        
        # Update Generator Config
        self.time_gen.fas_config = self.fas_data 
        
        if "range" in active:
            self.content_container.add_widget(self.time_gen.render_range(ui_conf.get("range_module", {})))
        
        if "duration" in active:
            self.content_container.add_widget(self.time_gen.render_duration(ui_conf.get("duration_module", {})))

        if "checkboxes" in active:
            self.content_container.add_widget(Label(text="[Checkboxes coming soon]", color=(0,0,0,1), size_hint_y=None, height='30dp'))
        if "tags" in active:
            self.content_container.add_widget(Label(text="[Tags coming soon]", color=(0,0,0,1), size_hint_y=None, height='30dp'))

    def save_record(self, *args):
        Logger.info("[ACTION] Save pressed (Logic coming soon)")