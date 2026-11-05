from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.core.utils import validate_amount
from valutatrade_hub.parser_service.config import ParserConfig


class BaseApiClient(ABC):
    source = "API"

    def __init__(self, config=None):
        self.config = config if config is not None else ParserConfig()

    @abstractmethod
    def fetch_rates(self) -> dict:
        pass

    def _get_json(self, url, params=None, headers=None):
        """Отправляет запрос и проверяет, наличие ошибок"""
        try:
            # отправляем запрос, если всё ок - возвращаем данные в словаре
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.config.REQUEST_TIMEOUT,
            )
        # если что-то пошло не так
        except requests.exceptions.RequestException:
            # Исходная ошибка может содержать URL с API-ключом.
            raise ApiRequestError(
                f"{self.source}: ошибка сети или превышено время ожидания"
            ) from None
        # если запрос ушёл, но со статусом что-то не так
        if response.status_code != 200:
            reasons = {
                401: "Проверьте API-ключ",
                403: "Доступ запрещён; проверьте API-ключ",
                429: "Превышен лимит запросов",
            }
            reason = reasons.get(
                response.status_code,
                "сервер не отвечает",
            )

            raise ApiRequestError(
                f"{self.source}: HTTP {response.status_code}, {reason}"
            )
        # смотрим ответ
        try:
            data = response.json()
        # если с JSON что-то не так
        except ValueError:
            raise ApiRequestError(
                f"{self.source}: сервер вернул некорректный JSON"
            ) from None
        # если (что странно), пришёл не JSON
        if not isinstance(data, dict):
            raise ApiRequestError(
                f"{self.source}: ожидался JSON-объект"
            )

        return data


class CoinGeckoClient(BaseApiClient):
    '''
    Класс для получения криптовалют из CoinGecko
    '''
    source = "CoinGecko"

    def fetch_rates(self) -> dict:
        base = self.config.BASE_CURRENCY

        try:
            # смотрим идентификаторы
            ids = [
                self.config.CRYPTO_ID_MAP[code]
                for code in self.config.CRYPTO_CURRENCIES
            ]
            # соединяем строки и приводим к нужному виду
            params = {
                "ids": ",".join(ids),
                "vs_currencies": base.lower(),
            }

            headers = {}
            if self.config.COINGECKO_API_KEY:
                headers["x-cg-demo-api-key"] = self.config.COINGECKO_API_KEY
            # получаем данные
            data = self._get_json(
                self.config.COINGECKO_URL,
                params=params,
                headers=headers,
            )

            rates = {}
            # преобразуем
            for code in self.config.CRYPTO_CURRENCIES:
                coin_id = self.config.CRYPTO_ID_MAP[code]
                rate = validate_amount(data[coin_id][base.lower()])

                rates[f"{code}_{base}"] = rate

        except (KeyError, TypeError, ValueError) as error:
            raise ApiRequestError(
                f"{self.source}: некорректные курсы "
                "или настройки ID валют"
            ) from error

        return rates


class ExchangeRateApiClient(BaseApiClient):
    source = "ExchangeRate-API"

    def fetch_rates(self) -> dict:
        if not self.config.EXCHANGERATE_API_KEY:
            raise ApiRequestError(
                "Не задана переменная окружения EXCHANGERATE_API_KEY"
            )

        base = self.config.BASE_CURRENCY

        url = (
            f"{self.config.EXCHANGERATE_API_URL}/"
            f"{self.config.EXCHANGERATE_API_KEY}/latest/{base}"
        )

        data = self._get_json(url)

        if data.get("result") != "success":
            error_type = data.get("error-type", "unknown-error")
            raise ApiRequestError(f"{self.source}: {error_type}")

        if data.get("base_code") != base:
            raise ApiRequestError(
                f"{self.source}: неожиданная базовая валюта"
            )

        try:
            rates = {}

            for code in self.config.FIAT_CURRENCIES:
                rate = validate_amount(data["conversion_rates"][code])

                # API возвращает USD → валюта.
                # Для нашего хранилища нужна валюта → USD.
                rates[f"{code}_{base}"] = 1 / rate

        except (KeyError, TypeError, ValueError) as error:
            raise ApiRequestError(
                f"{self.source}: некорректные курсы в ответе"
            ) from error

        return rates