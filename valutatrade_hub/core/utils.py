import json
from valutatrade_hub.core.constants import DATA_DIR, EXCHANGE_RATES


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

### ПОКА РАБОТАЕТ С КОНСТАНТОЙ - ПОТОМ ПОМЕНЯТЬ!!!
def get_rate(from_currency, to_currency):
    if not isinstance(from_currency, str) or not from_currency.strip():
        raise ValueError("Исходная валюта должна быть непустой строкой")

    if not isinstance(to_currency, str) or not to_currency.strip():
        raise ValueError("Целевая валюта должна быть непустой строкой")

    source = from_currency.strip().upper()
    target = to_currency.strip().upper()

    if source not in EXCHANGE_RATES:
        raise ValueError(f"Неизвестная валюта '{source}'")
    if target not in EXCHANGE_RATES:
        raise ValueError(f"Неизвестная валюта '{target}'")
    
    rate = EXCHANGE_RATES[source] / EXCHANGE_RATES[target]
    
    return {"rate": rate}