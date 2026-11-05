import json
from datetime import UTC, datetime

from valutatrade_hub.core.constants import DATA_DIR
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.infra.settings import SettingsLoader


def parser_get(source, target):
    """Должна получать свежий числовой курс из Parser Service."""
    raise ApiRequestError(
        f"Parser Service пока не подключён; "
        f"не удалось обновить курс {source}→{target}"
    )
def load_json(filename, default=None):
    """
    Загружает переданные данные из JSON.
    """
    # Проблема: иногда нам нужен не [], а {}
    # Фикс:
    if default is None:
        default = []
    
    path = DATA_DIR / filename

    try:
        with path.open(encoding="utf-8") as file:
            text = file.read()
            if not text.strip():
                return default.copy()
            return json.loads(text)

    except FileNotFoundError:
        return default.copy()

def save_json(filename, data):
    """
    Сохраняет переданные данные в JSON.
    """
    # parent создаёт недостающие папки - маловероятно, но пусть
    # exist_ok - не вызывает ошибки, если папка уже есть
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename
    #выполняем требование к атомарной записи
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
def get_rate(from_currency, to_currency):
    '''
    Вывод свежего курса одной валюты к другой и времени обновления
    '''
    # Да, необычный формат импорта, но иначе происходит ошибка
    from valutatrade_hub.core.currencies import get_currency
    # Проверяем вадиность
    source = get_currency(from_currency).code
    target = get_currency(to_currency).code

    # Создаём ключ по примеру
    key = f"{source}_{target}"
    # Для времени
    now = datetime.now(UTC)
        # Подгружает и ищем по ключу
    settings = SettingsLoader()
    filename = settings.get("RATES_FILE")
    if source == target:
        return {
            "rate": 1.0,
            "updated_at": now.isoformat(),
        }
    rates = load_json(filename, {})
    pairs = rates.get("pairs", {})
    record = pairs.get(key)
        # Например, для USD → BTC ищем сначала USD_BTC, затем BTC_USD.
    for pair_key in (key, f"{target}_{source}"):
        record = pairs.get(pair_key)
        if record is None:
            continue

        try:
            rate = validate_amount(record["rate"])
            updated = datetime.fromisoformat(record["updated_at"])

            # Старые записи без часового пояса считаем временем в UTC.
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=UTC)
        except (ValueError, TypeError, KeyError):
            # Если запись повреждена, проверяем следующую пару.
            continue

        # Принимаем только свежие записи с датой из прошлого или настоящего.
        age = (now - updated).total_seconds()
        if not 0 <= age < settings.get("RATES_TTL_SECONDS"):
            continue

        # Если нашли обратную пару, переворачиваем курс.
        if pair_key != key:
            rate = 1 / rate

        return {"rate": rate, "updated_at": updated.isoformat()}
    if source != "USD" and target != "USD":
        source_in_usd = get_rate(source, "USD")
        target_in_usd = get_rate(target, "USD")
        updated = min(
            datetime.fromisoformat(source_in_usd["updated_at"]),
            datetime.fromisoformat(target_in_usd["updated_at"]),
        )
        return {
            "rate": source_in_usd["rate"] / target_in_usd["rate"],
            "updated_at": updated.isoformat(),
        }
    # Свежего курса нет — пробуем обновить.
    try:
        rate = validate_amount(parser_get(source, target))
    except (OSError, ValueError, TypeError) as error:
        raise ApiRequestError(str(error)) from error

    record = {
        "rate": rate,
        "updated_at": datetime.now(UTC).isoformat(),
    }

    pairs[key] = record

    save_json(filename, {
        "pairs": pairs,
        "last_refresh": record["updated_at"],
    })

    return record.copy()
    

def normalize_currency(currency_code):
    '''
    Приводит код валют к общему виду
    '''
    if not isinstance(currency_code, str) or not currency_code.strip():
        raise ValueError("Код валюты должен быть непустой строкой")

    return currency_code.strip().upper()

# Много раз повторял вручную этот блок, решил, что можно вынести в def
def validate_amount(amount):
    '''
    Проверка на положительность числа
    '''
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Значение должно быть положительным числом")
    return float(amount)
