# Path: mobile_app/main.py
# Version: 1.0
# Description: Точка входа в приложение. Инициализация экранов и навигации.

import os
import sys

# Обеспечиваем корректный путь для импортов, если запускаем из папки mobile_app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

# Импортируем схему, чтобы инициализировать пути при старте
from core import mobile_schema

# Импорты экранов
from ui.screens.home import HomeScreen
from ui.screens.settings import SettingsScreen
from ui.screens.debug import DebugScreen
from ui.layouts.navigation import BottomNavBar

class LifeLoggerApp(App):
    def build(self):
        self.title = "Life Logger"
        
        # Основной контейнер
        root = BoxLayout(orientation='vertical')
        
        # Менеджер экранов
        # Используем NoTransition для мгновенного переключения (опционально)
        self.sm = ScreenManager(transition=NoTransition())
        
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(DebugScreen(name='debug'))
        
        root.add_widget(self.sm)
        
        # Навигационная панель
        nav_bar = BottomNavBar()
        nav_bar.manager = self.sm
        root.add_widget(nav_bar)
        
        return root

    def on_pause(self):
        # Для Android: разрешаем приложению уходить в фон без убийства
        return True

    def on_resume(self):
        pass

if __name__ == '__main__':
    LifeLoggerApp().run()