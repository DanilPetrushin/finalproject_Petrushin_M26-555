from pathlib import Path
from currencies import FiatCurrency, CryptoCurrency 

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
CURRENCIES = {
    "USD": FiatCurrency(
        name="US Dollar",
        code="USD",
        issuing_country="United States",
    ),
    "EUR": FiatCurrency(
        name="Euro",
        code="EUR",
        issuing_country="Eurozone",
    ),
    "RUB": FiatCurrency(
        name="Russian Ruble",
        code="RUB",
        issuing_country="Russia",
    ),
    "BTC": CryptoCurrency(
        name="Bitcoin",
        code="BTC",
        algorithm="SHA-256",
        market_cap=1.12e12,
    ),
    "ETH": CryptoCurrency(
        name="Ethereum",
        code="ETH",
        algorithm="Proof of Stake",
        market_cap=3.6e11,
    ),
}