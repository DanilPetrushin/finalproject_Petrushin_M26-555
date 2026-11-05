from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError
from valutatrade_hub.core.utils import normalize_currency


class Currency(ABC):
    def __init__(self, name, code):
        # Проверки перед присвоением
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название валюты должно быть непустой строкой")
        code = normalize_currency(code)
        if not 2 <= len(code) <= 5:
            raise ValueError("Код валюты должен содержать от 2 до 5 символов")
        if any(char.isspace() for char in code):
            raise ValueError("Код валюты не должен содержать пробелы")
        # Присвоение
        self.name = name.strip()
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        """Возвращает описание валюты для интерфейса и логов."""


class FiatCurrency(Currency):
    def __init__(self, name, code, issuing_country):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return (
            f"[FIAT] {self.code} — {self.name} "
            f"(Issuing: {self.issuing_country})"
        )


class CryptoCurrency(Currency):
    def __init__(self, name, code, algorithm, market_cap):
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = float(market_cap)

    def get_display_info(self) -> str:
        #преобразуем в формат 1.12е+12, и заменяем е+ на е
        market_cap = f"{self.market_cap:.2e}".replace("e+", "e")

        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {market_cap})"
        )




def get_currency(code: str) -> Currency:
    code = normalize_currency(code)

    if code not in CURRENCIES:
        raise CurrencyNotFoundError(code)

    return CURRENCIES[code]

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