# Path: mobile_app/ui/layouts/navigation.py
# Version: Kivy_1.0
# Description: Нижняя навигационная панель (стандартные виджеты).

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.logger import Logger

class BottomNavBar(BoxLayout):
    manager = ObjectProperty(None)  # Ссылка на ScreenManager

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '60dp'  # Фиксированная высота
        self.padding = 5
        self.spacing = 5
        
        # Кнопки навигации (используем Emojis для простоты)
        self.add_nav_btn("Ввод", "📝", "home")
        self.add_nav_btn("Настройки", "⚙️", "settings")
        self.add_nav_btn("Debug", "🐞", "debug")

    def add_nav_btn(self, text, icon, screen_name):
        # Кнопка с текстом (Icon + Text)
        btn = Button(
            text=f"{icon}\n{text}",
            halign='center',
            valign='middle',
            background_color=(0.2, 0.2, 0.2, 1) # Темно-серый
        )
        btn.bind(on_release=lambda x: self.switch_screen(screen_name))
        self.add_widget(btn)

    def switch_screen(self, screen_name):
        if self.manager:
            Logger.info(f"[UI LOG] Navigating to: {screen_name}")
            self.manager.current = screen_name