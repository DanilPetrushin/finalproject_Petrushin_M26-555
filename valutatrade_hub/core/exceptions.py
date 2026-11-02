class InsufficientFundsError(ValueError):
    def __init__(self, available, required, code):
        super().__init__(
            f"Недостаточно средств: доступно {available:.4f} {code}, "
            f"требуется {required:.4f} {code}"
        )


class CurrencyNotFoundError(ValueError):
    def __init__(self, code):
        super().__init__(f"Неизвестная валюта '{code}'")


class ApiRequestError(Exception):
    def __init__(self, reason):
        super().__init__(
            f"Ошибка при обращении к внешнему API: {reason}"
        )