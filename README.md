# Описание проекта
Данный проект представляет собой платформу для отслеживания и симуляции торговли валютами. Данная платформа позволяет пользователям регистрироваться, входить в аккаунт, совершать сделки по покуке/продаже фиатных и крипто валют, а также отслеживать курсы в реальном времени.
# Демонстрация работы
https://disk.yandex.ru/i/9CAFZXruK3usIA - копия на яндекс.диске
https://drive.google.com/file/d/1FA79wRlxMSAhId1YGymxEJQ88gvcjHVg/view?usp=sharing - копия на гугл.диске
# Установка и запуск
Для работы необходимы Git и менеджер пакетов uv. Проект использует Python версии 3.12 или новее.
1. Клонируйте репозиторий и перейдите в каталог проекта
```bash
git clone https://github.com/DanilPetrushin/finalproject_Petrushin_M26-555.git
cd finalproject_Petrushin_M26-555
```
2. Установите проект и зависимости
```bash
uv sync
```
3. Перейдите на следующие сайты и получите персональный API-ключ.
- https://www.exchangerate-api.com/ - ExchangeRate-API
- https://www.coingecko.com/en/api - CoinGecko
4. Задайте ключи в Bash.
```bash
export EXCHANGERATE_API_KEY="ваш_ключ"
export COINGECKO_API_KEY="ваш_ключ"
```
5. Запустите приложение
```bash
uv run valutatrade
```
Внутри приложения команда `help` показывает список команд, а `exit` завершает работу.

# Инструкция по использованию  
Команды:
```text
register --username <имя> --password <пароль> — регистрация
login --username <имя> --password <пароль> — вход
show-portfolio — показать портфель в USD
show-portfolio --base <валюта> — показать портфель в другой валюте
buy --currency <валюта> --amount <количество> — купить валюту
sell --currency <валюта> --amount <количество> — продать валюту
get-rate --from <валюта> --to <валюта> — получить курс
update-rates — обновить курсы из всех источников
update-rates --source <coingecko|exchangerate> — обновить источник
show-rates [--currency <код>] [--top <число>] [--base <код>] — показать курсы из кеша
test-fund — начислить 1000 тестовых USD
help — показать эту справку
exit — завершить работу
```
# Набор команд для проверки работы сервиса
Введи команды по очереди внутри приложения. Для примеров с EUR требуется успешное обновление курсов ExchangeRate-API.
```text
register --username test_wallet --password 1234
login --username test_wallet --password 1234
update-rates 
test-fund
buy --currency BTC --amount 0.01
buy --currency EUR --amount 12
sell --currency EUR --amount 2
show-portfolio
show-portfolio --base BTC
get-rate --from EUR --to BTC
show-rates
show-rates --currency EUR
show-rates --top 2
exit
```
# Кэш и данные
Рабочие JSON-файлы создаются при первом сохранении соответствующих данных.
- `data/rates.json` хранит последние курсы. По умолчанию курс считается свежим 300 секунд. Этот срок задаёт  `RATES_TTL_SECONDS` в `config.json`. 
- Если курс отсутствует или устарел, выполните `update-rates` и повторите команду.
- `data/exchange_rates.json` хранит историю измерений с временем и источником.
- `data/users.json` и `data/portfolios.json` хранят аккаунты и кошельки соответственно. 
- `logs/actions.log` содержит журнал операций, а `logs/parser.log` — журнал обновлений курсов.
# Структура проекта
- `valutatrade_hub/cli/`- файлы в данной папке отвечают за консольный интерфейс и разбор команд
- `valutatrade_hub/core/` - здесь хранятся ключевые классы  пользователя, кошелька и портфеля, а также функции необходимые для работы программы
- `valutatrade_hub/infra/settings.py`	- отвечает за загрузку настроек из `config.json`
- `valutatrade_hub/parser_service/` - API-клиенты, обновление кеша и запись истории
- `valutatrade_hub/logging_config.py` и `decorators.py` - отвечают за логирование