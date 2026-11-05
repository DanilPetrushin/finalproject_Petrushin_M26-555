import os

from valutatrade_hub.infra.settings import PROJECT_ROOT, SettingsLoader


class ParserConfig:
    def __init__(self):
        settings = SettingsLoader()
        # Ключи загружаются из переменной окружения
        self.EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "")
        self.COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

        # Эндпоинты
        self.COINGECKO_URL = ("https://api.coingecko.com/api/v3/simple/price")
        self.EXCHANGERATE_API_URL = ("https://v6.exchangerate-api.com/v6")

        # Списки валют
        self.BASE_CURRENCY = "USD"
        self.FIAT_CURRENCIES = ("EUR", "RUB")
        self.CRYPTO_CURRENCIES = ("BTC", "ETH")
        self.CRYPTO_ID_MAP = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
        }

        data_dir = PROJECT_ROOT / settings.get("DATA_DIR")

        self.RATES_FILE_PATH = data_dir / settings.get("RATES_FILE")
        self.HISTORY_FILE_PATH = data_dir / settings.get(
            "HISTORY_FILE", "exchange_rates.json"
            )

        
        # Сетевые параметры
        self.REQUEST_TIMEOUT = 10