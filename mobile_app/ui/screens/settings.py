from kivy.uix.label import Label
from .base_screen import BaseScreen

class SettingsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.add_widget(Label(text="Настройки (Скоро)", color=(0,0,0,1)))