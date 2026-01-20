# Path: mobile_app/core/sync_client.py
# Version: 1.2
# Description: Клиент. Добавлен метод получения хэша.

import requests
import json

class SyncClient:
    def __init__(self, server_url):
        self.base_url = server_url.rstrip("/")

    def check_connection(self):
        try:
            resp = requests.get(f"{self.base_url}/status", timeout=2)
            if resp.status_code == 200: return True, resp.json()
            return False, f"HTTP {resp.status_code}"
        except Exception as e: return False, str(e)

    def get_config_hash(self):
        """Запрашивает хэш конфига с сервера"""
        try:
            resp = requests.get(f"{self.base_url}/config/hash", timeout=3)
            if resp.status_code == 200:
                return resp.json().get("hash")
            return None
        except: return None

    def get_config(self):
        try:
            resp = requests.get(f"{self.base_url}/config/fas", timeout=3)
            return resp.json() if resp.status_code == 200 else None
        except: return None

    def push_data(self, records):
        try:
            resp = requests.post(f"{self.base_url}/sync/push", json=records, timeout=5)
            return resp.status_code == 200
        except: return False

    def pull_changes(self, since=None):
        try:
            url = f"{self.base_url}/sync/pull"
            if since: url += f"?since={since}"
            resp = requests.get(url, timeout=5)
            return resp.json() if resp.status_code == 200 else None
        except: return None