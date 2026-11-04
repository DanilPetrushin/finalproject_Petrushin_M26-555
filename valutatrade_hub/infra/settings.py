import json
from pathlib import Path
from typing import Any


# тут мы получаем именно путь до папки project на каждом пк
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# а вот тут уже до project/config
CONFIG_PATH = PROJECT_ROOT / "config.json"


class SettingsLoader:
    _instance = None # Атрибут для хранения единственного экземпляра

    def __new__(cls, *args, **kwargs):
        # Используем __new__, тк в рамках поставленной задачи
        # Этот способ является наиболее подходящим и (субъективно) понятным
        if cls._instance is None:
            # Создаём экземпляр
            instance = super().__new__(cls)
            instance._config = instance._load_config()
            cls._instance = instance

        return cls._instance

    def _load_config(self):
        # Значения на случай отсутствия файла
        config = {
            "DATA_DIR": "data",
            "USERS_FILE": "users.json",
            "PORTFOLIOS_FILE": "portfolios.json",
            "RATES_FILE": "rates.json",
            "RATES_TTL_SECONDS": 300,
            "DEFAULT_BASE_CURRENCY": "USD",
            "LOG_FILE": "logs/actions.log",
            "LOG_FORMAT": "%(message)s",
            "LOG_LEVEL": "INFO",
            "LOG_MAX_BYTES": 1048576,
            "LOG_BACKUP_COUNT": 3
            }

        try:
            with CONFIG_PATH.open(encoding="utf-8") as file:
                loaded_config = json.load(file)
        except FileNotFoundError:
            return config

        if not isinstance(loaded_config, dict):
            raise ValueError("config.json должен содержать JSON-объект")

        # Настройки из файла заменяют значения по умолчанию.
        config.update(loaded_config)

        return config

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)