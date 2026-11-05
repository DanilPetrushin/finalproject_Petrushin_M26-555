import json
import logging
from datetime import UTC, datetime

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.core.utils import load_json
from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.logging_config import get_action_logger


class RatesUpdater:
    def __init__(self, clients, storage):
        # Принимаем API и хранилища
        self.clients = list(clients)
        self.storage = storage

        if not self.clients:
            raise ValueError("Не указаны API-клиенты")

        self.logger = get_action_logger(
            name="valutatrade.parser",
            log_file=SettingsLoader().get(
                "PARSER_LOG_FILE",
                "logs/parser.log",
            ),
        )

    def _log(self, message, level=logging.INFO):
        # Можно было без этого, но решилвынести запись логов сюда, 
        # тк далее она повторяется несколько раз
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": logging.getLevelName(level),
            "message": message,
        }

        self.logger.log(
            level,
            "%s",
            json.dumps(entry, ensure_ascii=False),
        )

    def run_update(self):
        self._log("Начало обновления курсов")

        updated = 0     # Сколько пар обновили в кеше
        successful = 0  # Сколько источников удалось обработать
        errors = {}

        # По очереди обращаемся к каждому источнику
        for client in self.clients:
            source = client.source
            self._log(f"{source}: получение курсов")

            try:
                rates = client.fetch_rates()

                if not rates:
                    raise ApiRequestError(
                        f"{source}: получен пустой список курсов"
                    )

                self._log(
                    f"{source}: получено курсов: {len(rates)}; сохранение"
                )
                count = self.storage.save_rates(rates, source)

            except (ApiRequestError, OSError, ValueError) as error:
                errors[source] = str(error)
                self._log(f"{source}: {error}", logging.ERROR)

                # Допустим, один источник не сработал, тогда см следующий
                continue

            # Считаем источник успешным после сохранения данных
            updated += count
            successful += 1

            self._log(f"{source}: обновлено пар: {count}")
        # Но может быть такое, что ни один источник не сработал,
        # Тогда перенаправляем ошибку в CLI
        if successful == 0:
            self._log(
                "Обновление не выполнено: "
                "все источники завершились с ошибками",
                logging.ERROR,
            )
            raise ApiRequestError("; ".join(errors.values()))

        cache = load_json(self.storage.config.RATES_FILE_PATH, {})
        
        result = {
            "updated": updated,
            "errors": errors,
            "last_refresh": cache.get("last_refresh"),
        }

        self._log(
            f"Обновление завершено: обновлено пар: {updated}, "
            f"ошибок: {len(errors)}"
        )

        return result