from kivy.uix.label import Label
from .base_screen import BaseScreen

class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        self.add_widget(Label(text="Экран Ввода (Скоро)", color=(0,0,0,1)))