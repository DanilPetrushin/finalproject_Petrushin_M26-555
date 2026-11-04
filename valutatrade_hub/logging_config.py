import logging
from logging.handlers import RotatingFileHandler
from valutatrade_hub.infra.settings import PROJECT_ROOT, SettingsLoader
# Хотя logging и logging.handlers не упомянуты, как разрешённые библиотеки
# Они являются базовыми для решения подобных задач, поэтому я их изучил
# И реализовал решения ведения логов с их помощью   
# Источники: https://habr.com/ru/companies/wunderfund/articles/683880/
# https://docs-python.ru/standart-library/paket-logging-python/obekt-logger-modulja-logging/#logger.propagate


def get_action_logger():
    logger = logging.getLogger("valutatrade.actions")

    # Проверяем  наличие handler, чтобы не создавать его каждый раз
    if logger.handlers:
        return logger

    settings = SettingsLoader()
    log_path = PROJECT_ROOT / settings.get("LOG_FILE")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Тут создаём handler
    handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=settings.get("LOG_MAX_BYTES", 1048576),
        backupCount=settings.get("LOG_BACKUP_COUNT", 3),
        encoding="utf-8",
    )
    # Задаём оформление
    formatter = logging.Formatter(settings.get("LOG_FORMAT"))
    handler.setFormatter(formatter)
    # Всего есть 5 уровней: debug, info, warning, error и critical
    logger.setLevel(settings.get("LOG_LEVEL", "INFO"))
    logger.addHandler(handler)


    logger.propagate = False

    return logger