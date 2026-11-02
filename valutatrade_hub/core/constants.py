from pathlib import Path


DATA_DIR = Path("data")
# ЗАГЛУШКА
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "RUB": 0.01,
    "BTC": 60000.0,
    "ETH": 3000.0,
}
# Максимум времени с прошшлого обновления в секундах
TIME_LIMIT = 300
# Временная константа для поддерживаемых валют, пока не придумаю решение
SUPPORTED_CURRENCIES = {"USD", "EUR", "RUB", "BTC", "ETH"}