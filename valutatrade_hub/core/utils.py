import json
from datetime import datetime, timezone
from valutatrade_hub.core.constants import DATA_DIR, TIME_LIMIT


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
            return json.load(file)

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
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_rate(from_currency, to_currency):
    # Да, необычный формат импорта, но иначе происходит ошибка.
    from valutatrade_hub.core.currencies import get_currency
    # Проверяем вадиность
    source = get_currency(from_currency).code
    target = get_currency(to_currency).code

    # Создаём ключ по примеру
    key = f"{source}_{target}"
    # Для времени
    now = datetime.now(timezone.utc)
    # Подгружает и ищем по ключу
    rates = load_json("rates.json", {})
    record = rates.get(key)

    # Сначала пробуем использовать сохранённый курс.
    # Есть ли запись?
    if record is not None:
        try:
            # если есть - см. значение
            rate = validate_amount(record["rate"])
            # Из строки в datetime 
            updated = datetime.fromisoformat(record["updated_at"])

            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            # Вычисляем сколько времени прошло
            time_passed = (now - updated).total_seconds()

            if 0 <= time_passed < TIME_LIMIT:
                return {
                    "rate": rate,
                    "updated_at": record["updated_at"],
                }

        except (ValueError, TypeError, KeyError):
            pass
    raise ValueError(
    f"Курс {source}→{target} недоступен. Повторите попытку позже."
    )

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