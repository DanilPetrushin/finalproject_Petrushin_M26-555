from valutatrade_hub.core.usecases import TradingService
import shlex
from valutatrade_hub.core.constants import CURRENCIES
from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)


# Потом можно в utils убрать
def print_help():
    print("\nКоманды:")
    print("register --username <имя> --password <пароль> — регистрация")
    print("login --username <имя> --password <пароль> — вход")
    print("show-portfolio — показать портфель в USD")
    print("show-portfolio --base <валюта> — показать портфель в другой валюте")
    print("buy --currency <валюта> --amount <количество> — купить валюту")
    print("sell --currency <валюта> --amount <количество> — продать валюту")
    print("get-rate --from <валюта> --to <валюта> — получить курс")
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
                print(f"Портфель пользователя '{result['username']}' (база: {result['base']}):")

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
                    description = "Оценочная стоимость покупки"

                else:
                    result = service.sell(currency, amount)
                    operation = "Продажа"
                    description = "Оценочная выручка"

                code = result["currency_code"]

                print(
                    f"{operation} выполнена: "
                    f"{result['amount']:.4f} {code} "
                    f"по курсу {result['rate']:.4f} USD/{code}"
                )

                print("Изменения в портфеле:")

                print(
                    f"- {code}: было {result['before']:.4f} "
                    f"→ стало {result['after']:.4f}"
                )

                print(f"{description}: {result['cost']:,.4f} USD")
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
                    f"Курс {source}→{target}: {rate:.4f} "
                    f"(обновлено: {result['updated_at']})"
                )
                print(
                    f"Обратный курс {target}→{source}: "
                    f"{1 / rate:.4f}"
                )
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
            print("Повторите попытку позже. Если ошибка сохраняется, проверьте подключение к сети.")

        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")

        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break

if __name__ == "__main__":
    main()
