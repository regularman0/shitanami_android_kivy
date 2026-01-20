# Path: mobile_app/ui/generators/base.py
# Version: Kivy_1.0
# Description: Базовые компоненты UI для генераторов.

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line

class CardBox(BoxLayout):
    """Контейнер с фоном и рамкой"""
    def __init__(self, title="", bg_color=(0.95, 0.95, 0.95, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5
        self.size_hint_y = None
        # Высота будет вычисляться автоматически по контенту
        self.bind(minimum_height=self.setter('height'))

        # Рисуем фон и рамку
        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.8, 0.8, 0.8, 1) # Цвет рамки
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Заголовок
        if title:
            lbl = Label(text=title, color=(0.4, 0.4, 0.4, 1), font_size='14sp', 
                        size_hint_y=None, height='20dp', halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            self.add_widget(lbl)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.border.rectangle = (instance.x, instance.y, instance.width, instance.height)

class BaseGenerator:
    def __init__(self, theme, fas_config):
        self.theme = theme
        self.fas_config = fas_config