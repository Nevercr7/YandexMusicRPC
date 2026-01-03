"""
Управление настройками приложения
Сохраняет токен и другие настройки в JSON файл
"""

import os
import json
from typing import Optional

# Захардкоженный Discord Client ID для всех пользователей
DISCORD_CLIENT_ID = "1456892713621258319"

# Путь к файлу настроек в AppData
APPDATA_FOLDER = os.path.join(os.environ.get("APPDATA", ""), "YandexMusicRPC")
SETTINGS_FILE = os.path.join(APPDATA_FOLDER, "settings.json")

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "yandex_token": "",
    "update_interval": 5,
    "show_timestamp": True,
    "autostart": False,
    "minimize_to_tray": True,
    "first_run": True
}


def ensure_appdata_folder():
    """Создать папку в AppData если её нет"""
    if not os.path.exists(APPDATA_FOLDER):
        os.makedirs(APPDATA_FOLDER)


def load_settings() -> dict:
    """Загрузить настройки из файла"""
    ensure_appdata_folder()
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Добавляем недостающие ключи из дефолтных
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception:
            pass
    
    # Пробуем мигрировать токен из старого config.py
    try:
        import config
        if hasattr(config, 'YANDEX_MUSIC_TOKEN') and config.YANDEX_MUSIC_TOKEN:
            settings = DEFAULT_SETTINGS.copy()
            settings["yandex_token"] = config.YANDEX_MUSIC_TOKEN
            settings["first_run"] = False
            save_settings(settings)
            return settings
    except ImportError:
        pass
    
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """Сохранить настройки в файл"""
    ensure_appdata_folder()
    
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")


def get_token() -> str:
    """Получить токен Yandex Music"""
    settings = load_settings()
    return settings.get("yandex_token", "")


def set_token(token: str):
    """Установить токен Yandex Music"""
    settings = load_settings()
    settings["yandex_token"] = token
    settings["first_run"] = False
    save_settings(settings)


def is_first_run() -> bool:
    """Проверить, первый ли это запуск"""
    settings = load_settings()
    return settings.get("first_run", True) or not settings.get("yandex_token", "")


def get_update_interval() -> int:
    """Получить интервал обновления"""
    settings = load_settings()
    return settings.get("update_interval", 5)


def is_autostart_enabled() -> bool:
    """Проверить, включён ли автозапуск"""
    settings = load_settings()
    return settings.get("autostart", False)


def set_autostart_enabled(enabled: bool):
    """Установить состояние автозапуска в настройках"""
    settings = load_settings()
    settings["autostart"] = enabled
    save_settings(settings)
