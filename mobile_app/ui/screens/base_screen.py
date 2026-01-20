# Path: mobile_app/ui/screens/base_screen.py
# Version: Kivy_1.0
# Description: Базовый экран с белым фоном.

from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.logger import Logger

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Делаем белый фон (Kivy по умолчанию черный)
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1) # Почти белый
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.bind(on_enter=self._log_enter)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _log_enter(self, *args):
        Logger.info(f"[UI LOG] Entered screen: {self.name}")