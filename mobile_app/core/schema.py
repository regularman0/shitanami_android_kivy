# Path: mobile_app/core/schema.py
# Version: 1.0
# Description: Утилиты схемы для мобильного приложения (копия логики с ПК).

# Формат времени (без секунд)
DT_FMT = "%d.%m.%Y %H:%M"

def normalize_db_name(prefix, index):
    """
    Формирует имя: PREFIX + _ + INDEX.
    Гарантирует одно подчеркивание.
    """
    clean_prefix = prefix.rstrip("_")
    return f"{clean_prefix}_{index}"