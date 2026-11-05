import shlex

from prettytable import PrettyTable

from valutatrade_hub.core.currencies import CURRENCIES
from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.usecases import TradingService


# при желании можно в utils убрать, но здесь читаемость лучше
def print_help():
    print("\nКоманды:")
    print("register --username <имя> --password <пароль> — регистрация")
    print("login --username <имя> --password <пароль> — вход")
    print("show-portfolio — показать портфель в USD")
    print("show-portfolio --base <валюта> — показать портфель в другой валюте")
    print("buy --currency <валюта> --amount <количество> — купить валюту")
    print("sell --currency <валюта> --amount <количество> — продать валюту")
    print("get-rate --from <валюта> --to <валюта> — получить курс")
    print("update-rates — обновить курсы из всех источников")
    print("update-rates --source <coingecko|exchangerate> — обновить источник")
    print("show-rates [--currency <код>] [--top <число>] "
        "[--base <код>] — показать курсы из кеша")
    print("help — показать справку")
    print("exit — завершить работу")
    print('\nЗначения с пробелами заключайте в кавычки: "Иван Иванов".')


def main():
    service = TradingService()

    print("Добро пожаловать в ValutaTrade Hub!")
    print_help()

    while True:
        try:
            user_input = input("\nВведите команду: ").strip()
            args = shlex.split(user_input)

            if not args:
                continue

            command = args[0]

            if command == "exit":
                if len(args) != 1:
                    raise ValueError("Команда exit не принимает аргументы")
                print("До свидания!")
                break
            elif command == "help":
                if len(args) != 1:
                    raise ValueError("Команда help не принимает аргументы")

                print_help()
            elif command == "register":
                if (
                    len(args) != 5
                    or args[1] != "--username"
                    or args[3] != "--password"
                ):
                    raise ValueError(
                        "Использование: register "
                        "--username <имя> --password <пароль>"
                    )

                result = service.register(args[2], args[4])

                print(
                    f"Пользователь '{result['username']}' зарегистрирован "
                    f"(id={result['user_id']}). Теперь выполните login."
                )

            elif command == "login":
                if (
                    len(args) != 5
                    or args[1] != "--username"
                    or args[3] != "--password"
                ):
                    raise ValueError(
                        "Использование: login --username <имя> --password <пароль>"
                    )

                result = service.login(args[2], args[4])

                print(f"Вы вошли как '{result['username']}'")
            elif command == "show-portfolio":
                if len(args) == 1:
                    base = None

                elif len(args) == 3 and args[1] == "--base":
                    base = args[2]

                else:
                    raise ValueError(
                        "Использование: show-portfolio --base <валюта>"
                    )

                result = service.show_portfolio(base)

                if not result["wallets"]:
                    print("Ваш портфель пуст.")
                    continue
                
                #  См. методичка 2 часть ТЗ
                print(f"Портфель пользователя '{result['username']}'"
                      f" (база: {result['base']}):")

                for wallet in result["wallets"]:
                    print(
                        f"- {wallet['currency_code']}: "
                        f"{wallet['balance']:.4f} → "
                        f"{wallet['value']:.4f} {result['base']}"
                    )

                print("---------------------------------")
                print(
                    # Тысячи разделяем запятыми
                    f"ИТОГО: {result['total']:,.4f} "
                    f"{result['base']}"
                )
            elif command in ("buy", "sell"):
                if (
                    len(args) != 5
                    or args[1] != "--currency"
                    or args[3] != "--amount"
                ):
                    raise ValueError(
                        f"Использование: {command} "
                        "--currency <валюта> --amount <количество>"
                    )

                currency = args[2]

                try:
                    amount = float(args[4])
                except ValueError as error:
                    raise ValueError(
                        "'amount' должен быть положительным числом"
                    ) from error

                if command == "buy":
                    result = service.buy(currency, amount)
                    operation = "Покупка"
                    description = "Списано с USD-кошелька"
                else:
                    result = service.sell(currency, amount)
                    operation = "Продажа"
                    description = "Зачислено на USD-кошелёк"

                code = result["currency_code"]

                print(
                    f"{operation} выполнена: "
                    f"{result['amount']:.8f} {code} "
                    f"по курсу {result['rate']:.8f} USD/{code}"
                )

                print("Изменения в портфеле:")
                print(
                    f"- {code}: было {result['before']:.8f} "
                    f"→ стало {result['after']:.8f}"
                )

                print(f"{description}: {result['cost']:,.8f} USD")
            elif command == "get-rate":
                if (
                    len(args) != 5
                    or args[1] != "--from"
                    or args[3] != "--to"
                ):
                    raise ValueError(
                        "Использование: get-rate "
                        "--from <валюта> --to <валюта>"
                    )

                result = service.get_rate(args[2], args[4])

                source = result["from_currency"]
                target = result["to_currency"]
                rate = result["rate"]

                print(
                    f"Курс {source}→{target}: {rate:.8f} "
                    f"(обновлено: {result['updated_at']})"
                )
                print(
                    f"Обратный курс {target}→{source}: "
                    f"{1 / rate:.8f}"
                )
            elif command == "update-rates":
                if len(args) == 1:
                    source = None

                elif len(args) == 3 and args[1] == "--source":
                    source = args[2]

                else:
                    raise ValueError(
                        "Использование: update-rates "
                        "[--source coingecko|exchangerate]"
                    )

                result = service.update_rates(source)

                if result["errors"]:
                    print(
                        "Обновление завершено с ошибками. "
                        f"Обновлено пар: {result['updated']}."
                    )

                    for name, message in result["errors"].items():
                        print(f"- {name}: {message}")

                else:
                    print(
                        "Обновление завершено. "
                        f"Обновлено пар: {result['updated']}."
                    )

                print(
                    f"Последнее обновление кеша: "
                    f"{result['last_refresh']}"
                )
            elif command == "show-rates":

                # Здесь удобно: аргументы без самой команды идут парами
                # Так что проверяем на пары
                if (len(args) - 1) % 2 != 0:
                    raise ValueError("Использование: show-rates "
                    "[--currency <код>] [--top <число>] [--base <код>]")
                options = {}

                # 1, 3, 5 - это параметры (не значения), проверяем их:
                # Возможен ли такой параметр?
                # Не встречался ли он преждде?
                for i in range(1, len(args), 2):
                    flag = args[i]

                    if (
                        flag not in ("--currency", "--top", "--base")
                        or flag in options
                    ):
                        raise ValueError("Использование: show-rates "
                        "[--currency <код>] [--top <число>] [--base <код>]")

                    options[flag] = args[i + 1]
                
                # Смотрим значение параметра top, тк к нему есть ряд требований
                top = options.get("--top")
                # Если оно всё же есть:
                if top is not None:
                    try:
                        top = int(top)
                    except ValueError:
                        raise ValueError(
                            "'top' должен быть положительным целым числом"
                        ) from None
                if top <= 0:
                    raise ValueError("'top' должен быть положительным целым числом")
                
                result = service.show_rates(
                    currency=options.get("--currency"),
                    top=top,
                    base=options.get("--base"),
                )

                print(f"Курсы из кеша, база: {result['base']}")
                print(
                    f"Последнее обновление кеша: "
                    f"{result['last_refresh']}"
                )

                # Делаем таблицу
                table = PrettyTable()
                table.field_names = ["Валюта", "Курс", "Обновлено"]

                for row in result["rates"]:
                    table.add_row([
                        row["currency_code"],
                        f"{row['rate']:.8f}",
                        row["updated_at"],
                    ])

                print(table)
            else:
                print(f"Команды '{command}' нет. Введите help.")

        # Перехват ошибок от частного к общему
        except InsufficientFundsError as error:
            print(error)

        except CurrencyNotFoundError as error:
            print(error)
            print("Поддерживаемые валюты: " + ", ".join(CURRENCIES))

        except ApiRequestError as error:
            print(error)
            print("Повторите попытку позже. Если ошибка сохраняется, "
                  "проверьте подключение к сети.")

        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")

        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break

if __name__ == "__main__":
    main()
