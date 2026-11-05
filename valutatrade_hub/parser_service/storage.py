from datetime import UTC, datetime

from valutatrade_hub.core.utils import (
    load_json,
    normalize_currency,
    save_json,
    validate_amount,
)
from valutatrade_hub.parser_service.config import ParserConfig


def _utc_time(value):
    """Преобразует строковую дату в datetime с часовым поясом UTC."""
    result = datetime.fromisoformat(value)

    if result.tzinfo is None:
        result = result.replace(tzinfo=UTC)

    return result.astimezone(UTC)


class RatesStorage:
    def __init__(self, config=None):
        self.config = config if config is not None else ParserConfig()

    def save_rates(self, rates, source, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now(UTC).isoformat()

        moment = _utc_time(timestamp)
        timestamp = moment.isoformat().replace("+00:00", "Z")

        # Сначала проверяем все входные данные.
        records = []

        for pair, rate in rates.items():
            source_code, target_code = pair.split("_")

            source_code = normalize_currency(source_code)
            target_code = normalize_currency(target_code)

            for code in (source_code, target_code):
                if (
                    not 2 <= len(code) <= 5
                    or any(char.isspace() for char in code)
                ):
                    raise ValueError(f"Некорректный код валюты '{code}'")

            pair = f"{source_code}_{target_code}"

            records.append({
                "id": f"{pair}_{timestamp}",
                "from_currency": source_code,
                "to_currency": target_code,
                "rate": validate_amount(rate),
                "timestamp": timestamp,
                "source": source,
                "meta": {},
            })

        history = load_json(self.config.HISTORY_FILE_PATH, [])
        cache = load_json(
            self.config.RATES_FILE_PATH,
            {"pairs": {}, "last_refresh": None},
        )

        if not isinstance(history, list) or not isinstance(cache, dict):
            raise TypeError("Некорректный формат хранилища курсов")
        if "pairs" in cache:
            pairs = cache["pairs"]
        else:
            # Переносим записи из прежнего плоского формата кеша.
            pairs = {
                key: value
                for key, value in cache.items()
                if isinstance(value, dict) and "rate" in value
            }

        if not isinstance(pairs, dict):
            raise TypeError("Раздел 'pairs' должен быть словарём")

        known_ids = {item["id"] for item in history}

        added = 0
        updated = 0

        for record in records:
            # Повторное измерение с тем же id не добавляем.
            if record["id"] not in known_ids:
                history.append(record)
                known_ids.add(record["id"])
                added += 1

            pair = (
                f"{record['from_currency']}_"
                f"{record['to_currency']}"
            )
            previous = pairs.get(pair)

            # В кеше побеждает только более новая запись.
            if (
                previous is None
                or moment > _utc_time(previous["updated_at"])
            ):
                pairs[pair] = {
                    "rate": record["rate"],
                    "updated_at": timestamp,
                    "source": source,
                }
                updated += 1

        if added:
            save_json(self.config.HISTORY_FILE_PATH, history)

        if updated:
            cache = {
                "pairs": pairs,
                "last_refresh": datetime.now(UTC)
                .isoformat()
                .replace("+00:00", "Z"),
            }
            save_json(self.config.RATES_FILE_PATH, cache)

        return updated