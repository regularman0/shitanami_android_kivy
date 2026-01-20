# Path: mobile_app/core/synchronizer.py
# Version: 1.0
# Description: Логика двусторонней синхронизации.

from datetime import datetime
from .database import db
from .sync_client import SyncClient

class Synchronizer:
    def __init__(self, server_url):
        self.client = SyncClient(server_url)

    def sync_now(self):
        log = []
        
        # 1. Проверка связи
        ok, msg = self.client.check_connection()
        if not ok:
            return False, ["Нет связи с сервером"]

        # 2. PUSH (Отправка моих изменений)
        unsynced = db.get_unsynced()
        if unsynced:
            log.append(f"Отправка {len(unsynced)} записей...")
            success = self.client.push_data(unsynced)
            if success:
                ids = [r["id"] for r in unsynced]
                db.mark_as_synced(ids)
                log.append("✅ Отправлено успешно")
            else:
                log.append("❌ Ошибка отправки")
                return False, log
        else:
            log.append("Нет новых записей для отправки")

        # 3. PULL (Получение чужих изменений)
        last_sync = db.get_last_sync_time()
        log.append(f"Запрос изменений с: {last_sync or 'Начала времен'}")
        
        remote_data = self.client.pull_changes(last_sync)
        if remote_data is None:
            log.append("❌ Ошибка получения данных")
            return False, log
            
        records = remote_data.get("records", [])
        if records:
            log.append(f"Получено {len(records)} обновлений")
            count = 0
            for rec in records:
                # Помечаем как синхронизированные, так как они пришли с сервера
                rec["synced"] = 1
                if db.upsert_record(rec):
                    count += 1
            log.append(f"✅ Применено {count} записей")
        else:
            log.append("Нет обновлений на сервере")

        # 4. Обновление времени
        db.set_last_sync_time(datetime.now().isoformat())
        log.append("Синхронизация завершена")
        
        return True, log

    def sync_fas(self):
        """Скачивает FAS конфиг"""
        conf = self.client.get_config()
        return conf