# Path: mobile_app/ui/screens/settings.py
# Version: Kivy_1.3
# Description: Экран настроек. Исправлен краш при биндинге высоты лейбла.

import threading
import json
import os
from datetime import datetime

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivy.logger import Logger

from .base_screen import BaseScreen
from core import mobile_schema
from core.sync_client import SyncClient
from core.synchronizer import Synchronizer

class SettingsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        
        self.store = JsonStore(os.path.join(mobile_schema.CONFIG_DIR, 'app_settings.json'))
        self.blink_event = None # Для анимации
        
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.add_widget(self.layout)

        # 1. Заголовок
        lbl_title = Label(text="Настройки Связи", font_size='22sp', color=(0,0,0,1), 
                          size_hint_y=None, height='40dp', bold=True)
        self.layout.add_widget(lbl_title)

        # 2. IP Адрес
        ip_box = BoxLayout(orientation='vertical', size_hint_y=None, height='70dp', spacing=5)
        ip_box.add_widget(Label(text="IP Сервера (ПК):", color=(0.3,0.3,0.3,1), 
                                size_hint_y=None, height='20dp', halign='left', text_size=(self.width, None)))
        
        saved_ip = self.store.get('network')['ip'] if self.store.exists('network') else "http://192.168.0.103:8000"
        self.ti_ip = TextInput(text=saved_ip, multiline=False, size_hint_y=None, height='40dp', font_size='16sp', write_tab=False)
        ip_box.add_widget(self.ti_ip)
        self.layout.add_widget(ip_box)

        # 3. Кнопка Проверки
        btn_check = Button(text="Проверить связь", size_hint_y=None, height='45dp', background_color=(0.2, 0.6, 0.8, 1))
        btn_check.bind(on_release=self.check_connection)
        self.layout.add_widget(btn_check)

        # 4. Автоочистка
        clear_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        saved_clear = self.store.get('behavior')['auto_clear'] if self.store.exists('behavior') else False
        
        self.cb_clear = CheckBox(active=saved_clear, size_hint_x=None, width='40dp', color=(0,0,0,1))
        self.cb_clear.bind(active=self.save_settings)
        
        lbl_clear = Label(text="Очищать форму после сохранения", color=(0,0,0,1), halign='left', valign='middle')
        lbl_clear.bind(size=lbl_clear.setter('text_size'))
        
        clear_box.add_widget(self.cb_clear)
        clear_box.add_widget(lbl_clear)
        self.layout.add_widget(clear_box)

        # 5. Разделитель
        self.layout.add_widget(Label(size_hint_y=None, height='10dp'))

        # 6. Действия
        btn_sync = Button(text="СИНХРОНИЗАЦИЯ БД", size_hint_y=None, height='50dp', background_color=(0.3, 0.7, 0.3, 1))
        btn_sync.bind(on_release=self.do_sync)
        self.layout.add_widget(btn_sync)
        
        btn_dl = Button(text="Скачать структуру (FAS)", size_hint_y=None, height='45dp')
        btn_dl.bind(on_release=self.download_fas)
        self.layout.add_widget(btn_dl)

        # 7. Статус и Логи
        self.lbl_status = Label(text="Ожидание...", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height='30dp', bold=True)
        self.layout.add_widget(self.lbl_status)

        # --- ИСПРАВЛЕНИЕ ЛОГА (Scroll + Wrap) ---
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        
        self.lbl_log = Label(
            text="Лог операций...", 
            color=(0,0,0,1), 
            font_name="Roboto", 
            font_size='11sp', 
            size_hint_y=None, 
            halign='left', 
            valign='top'
        )
        
        # 1. При изменении ширины контейнера обновляем text_size лейбла
        self.lbl_log.bind(width=lambda *x: self.lbl_log.setter('text_size')(self.lbl_log, (self.lbl_log.width, None)))
        
        # 2. ИСПРАВЛЕНО: При изменении текстуры берем только ВЫСОТУ (индекс 1)
        def update_height(instance, value):
            instance.height = value[1]
            
        self.lbl_log.bind(texture_size=update_height)
        
        scroll.add_widget(self.lbl_log)
        self.layout.add_widget(scroll)

    # ================= LOGIC =================

    def save_settings(self, *args):
        ip = self.ti_ip.text.strip()
        auto_clear = self.cb_clear.active
        self.store.put('network', ip=ip)
        self.store.put('behavior', auto_clear=auto_clear)
        Logger.info("[SETTINGS] Saved")

    def _get_sync(self):
        # FIX: метод переименован (был _get_sync_manager) и реализован
        ip = self.ti_ip.text.strip()
        self.save_settings() # Save current IP
        return Synchronizer(ip)

    # --- Animation ---
    def _start_blink(self, text="Подключение..."):
        self.lbl_status.text = text
        self.lbl_status.color = (0.9, 0.6, 0, 1) # Orange
        if self.blink_event: self.blink_event.cancel()
        self.blink_event = Clock.schedule_interval(self._blink_tick, 0.5)

    def _stop_blink(self):
        if self.blink_event:
            self.blink_event.cancel()
            self.blink_event = None

    def _blink_tick(self, dt):
        # Мигаем прозрачностью или цветом
        current = self.lbl_status.color
        # Если оранжевый -> серый, иначе -> оранжевый
        if current[0] > 0.8: 
            self.lbl_status.color = (0.5, 0.5, 0.5, 1)
        else:
            self.lbl_status.color = (0.9, 0.6, 0, 1)

    # --- Check Connection ---
    def check_connection(self, instance):
        self._start_blink("Проверка связи...")
        threading.Thread(target=self._check_thread).start()

    def _check_thread(self):
        try:
            sync = self._get_sync()
            ok, msg = sync.client.check_connection()
            self._update_status_ui(ok, msg)
        except Exception as e:
            self._update_status_ui(False, f"Internal Error: {e}")

    @mainthread
    def _update_status_ui(self, ok, msg):
        self._stop_blink()
        if ok:
            srv = msg.get('server', 'Unknown') if isinstance(msg, dict) else 'Unknown'
            self.lbl_status.text = f"Успешно: {srv}"
            self.lbl_status.color = (0, 0.7, 0, 1)
        else:
            self.lbl_status.text = f"Ошибка: {msg}"
            self.lbl_status.color = (0.8, 0, 0, 1)

    # --- Sync DB ---
    def do_sync(self, instance):
        self._start_blink("Синхронизация...")
        self.lbl_log.text = "Запуск..."
        threading.Thread(target=self._sync_thread).start()

    def _sync_thread(self):
        try:
            sync = self._get_sync()
            ok, logs = sync.sync_now()
            self._update_sync_ui(ok, logs)
        except Exception as e:
            self._update_sync_ui(False, [f"Fatal Error: {e}"])

    @mainthread
    def _update_sync_ui(self, ok, logs):
        self._stop_blink()
        self.lbl_log.text = "\n".join(logs)
        if ok:
            self.lbl_status.text = "Синхронизация завершена"
            self.lbl_status.color = (0, 0.7, 0, 1)
        else:
            self.lbl_status.text = "Ошибка синхронизации"
            self.lbl_status.color = (0.8, 0, 0, 1)

    # --- Download FAS ---
    def download_fas(self, instance):
        self._start_blink("Скачивание конфига...")
        threading.Thread(target=self._download_thread).start()

    def _download_thread(self):
        try:
            client = self._get_sync().client
            
            # 1. Check Hash
            server_hash = client.get_config_hash()
            if not server_hash:
                self._update_download_ui(False, "Нет связи или хэша")
                return

            # 2. Compare with local (if implemented stored hash)
            # Для простоты - качаем всегда, если нажали кнопку
            
            conf = client.get_config()
            if conf:
                try:
                    # Пишем файл
                    with open(mobile_schema.FAS_PATH, "w", encoding="utf-8") as f:
                        json.dump(conf, f, ensure_ascii=False, indent=4)
                    self._update_download_ui(True, "FAS обновлен!")
                except Exception as e:
                    self._update_download_ui(False, f"Ошибка записи: {e}")
            else:
                self._update_download_ui(False, "Ошибка скачивания JSON")
        except Exception as e:
             self._update_download_ui(False, f"Error: {e}")

    @mainthread
    def _update_download_ui(self, ok, msg):
        self._stop_blink()
        self.lbl_status.text = msg
        self.lbl_status.color = (0, 0.7, 0, 1) if ok else (0.8, 0, 0, 1)