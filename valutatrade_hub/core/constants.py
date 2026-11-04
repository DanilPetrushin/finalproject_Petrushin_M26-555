from valutatrade_hub.infra.settings import PROJECT_ROOT, SettingsLoader


settings = SettingsLoader()
DATA_DIR = PROJECT_ROOT / settings.get("DATA_DIR")
TIME_LIMIT = settings.get("RATES_TTL_SECONDS")
# ЗАГЛУШКА
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "RUB": 0.01,
    "BTC": 60000.0,
    "ETH": 3000.0,
}