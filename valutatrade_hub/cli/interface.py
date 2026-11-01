from valutatrade_hub.core.usecases import TradingService
import shlex
def main():
    def print_help():
        print("\nКоманды:")
        print("register --username <имя> --password <пароль> — регистрация")
        print("login --username <имя> --password <пароль> — вход")
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
                            "Использование: login "
                            "--username <имя> --password <пароль>"
                        )

                    result = service.login(args[2], args[4])

                    print(f"Вы вошли как '{result['username']}'")

                else:
                    print(f"Команды '{command}' нет. Введите help.")

            except (ValueError, OSError) as error:
                print(f"Ошибка: {error}")

            except (EOFError, KeyboardInterrupt):
                print("\nДо свидания!")
                break

if __name__ == "__main__":
    main()
