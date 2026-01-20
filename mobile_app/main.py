# Path: mobile_app/main.py
# Version: Kivy_1.0
# Description: Точка входа Kivy. Содержит Crash Reporter.

import sys
import os
import traceback

# 1. Настройка путей (чтобы видеть core и ui)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Kivy Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.logger import Logger

# Пытаемся импортировать наши модули (внутри try/except)
try:
    from ui.layouts.navigation import BottomNavBar
    from ui.screens.home import HomeScreen
    from ui.screens.settings import SettingsScreen
    from ui.screens.debug import DebugScreen
    MODULES_LOADED = True
except Exception as e:
    MODULES_LOADED = False
    CRASH_TRACE = traceback.format_exc()

class LifeLoggerApp(App):
    def build(self):
        # Настройка окна для Android (чтобы клавиатура не перекрывала ввод)
        Window.softinput_mode = 'resize'
        self.title = "Life Logger"
        
        # Если модули не загрузились — показываем ошибку
        if not MODULES_LOADED:
            return self.build_crash_screen()

        try:
            # Главный контейнер (Вертикальный)
            root = BoxLayout(orientation='vertical')
            
            # Менеджер экранов (занимает всё свободное место)
            self.sm = ScreenManager()
            self.sm.add_widget(HomeScreen())
            self.sm.add_widget(SettingsScreen())
            self.sm.add_widget(DebugScreen())
            
            root.add_widget(self.sm)
            
            # Навигация (внизу)
            nav = BottomNavBar()
            nav.manager = self.sm # Связываем с менеджером
            root.add_widget(nav)
            
            Logger.info("[SYS LOG] UI Built successfully")
            return root
            
        except Exception as e:
            Logger.error(f"[SYS LOG] Build Error: {e}")
            return self.build_crash_screen(traceback.format_exc())

    def build_crash_screen(self, trace=None):
        """Экран смерти, если что-то пошло не так"""
        msg = trace if trace else CRASH_TRACE
        Logger.critical(f"[CRASH] {msg}")
        
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(
            text="CRITICAL ERROR", 
            color=(1, 0, 0, 1), 
            font_size='24sp', 
            size_hint_y=None, height=50
        ))
        layout.add_widget(Label(
            text=msg, 
            color=(1, 0, 0, 1),
            text_size=(Window.width - 40, None),
            halign='left',
            valign='top'
        ))
        return layout

if __name__ == '__main__':
    LifeLoggerApp().run()