import json
from datetime import datetime, timezone
from functools import wraps

from valutatrade_hub.logging_config import get_action_logger


def log_action(action, verbose=False):
    # Позднее через verbose будет добавляться контекст
    def decorator(function):
        @wraps(function)
        def wrapper(self, currency_code, amount):
            logger = get_action_logger()
            user = self.current_user

            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "INFO",
                "action": action.upper(),
                "username": user.username if user is not None else None,
                "currency_code": currency_code,
                "amount": amount,
                "rate": None, # Пока курс неизвестен
                "base": "USD",
            }

            # Вызываем исходный метод
            try:
                result = function(self, currency_code, amount)
            # Если получили ошибку в результате него выполнения
            except Exception as error:
                entry["result"] = "ERROR"
                entry["error_type"] = type(error).__name__
                entry["error_message"] = str(error)

                logger.info(
                    "%s",
                    json.dumps(entry, ensure_ascii=False, default=str),
                )

                # Как и сказано: не глотаем исключения
                raise

            # Если ошибки не произошло
            entry["currency_code"] = result["currency_code"]
            entry["amount"] = result["amount"]
            entry["rate"] = result["rate"]
            entry["result"] = "OK"

            if verbose:
                entry["before"] = result["before"]
                entry["after"] = result["after"]

            logger.info(
                "%s",
                json.dumps(entry, ensure_ascii=False, default=str),
            )

            return result

        return wrapper

    return decorator