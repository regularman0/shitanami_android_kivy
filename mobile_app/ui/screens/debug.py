from kivy.uix.label import Label
from .base_screen import BaseScreen

class DebugScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "debug"
        self.add_widget(Label(text="Debug Info (Скоро)", color=(0,0,0,1)))