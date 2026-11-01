#https://metanit.com/python/tutorial/6.9.php - про secrets
# Не указан, как раз разрешённый, однако является
# встроенным и используется для подобных задач
import secrets  
from datetime import datetime, timezone

from valutatrade_hub.core.models import Portfolio, User, Wallet
from valutatrade_hub.core.utils import load_json, save_json, get_rate


class TradingService:
    def __init__(self):
        self.current_user = None
        # Пока никто не вошёл current_user = None
    def register(self, username, password):
        users = load_json("users.json")

        if not isinstance(username, str) or not username.strip():
            raise ValueError("Неверное имя пользователя")

        username = username.strip()

        # Проверяем по всем строкам "username" в users.JSON 
        for item in users:
            if item["username"] == username:
                raise ValueError(
                    f"Имя пользователя '{username}' уже занято"
                )
        # Смотрим max значение user_id, если их нет вообще, то 0 -> +1
        user_id = max((item["user_id"] for item in users),default=0) + 1

        #Собираем экземпляр класса
        user = User (user_id = user_id,
                    username = username,
                    password = password, 
                    salt = secrets.token_hex(8), 
                    registration_date = datetime.now(timezone.utc))

        # get_user_info возвращает user_id, username и registration_date  
        # остальное добавляем вручную через методы
        user_data = user.get_user_info()
        user_data["hashed_password"] = user.hashed_password
        user_data["salt"] = user.salt
        # Добавляем запись в переменную users
        users.append(user_data)

        # Сразу создаём пустой портфель, чтобы закрепить его за юзером

        # Передаём user, тк в самом классе он достаёт user_id из user
        portfolio = Portfolio(user)
        portfolios = load_json("portfolios.json")
        portfolios.append({
            "user_id": portfolio.user.user_id,
            "wallets": portfolio.wallets,
        })

        # Сохраняем переменные с данными в JSON
        save_json("users.json", users)
        save_json("portfolios.json", portfolios)

        return user.get_user_info()
    
    def login(self, username, password):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Неверное имя пользователя")

        username = username.strip()

        users = load_json("users.json")

        for item in users:
            if item["username"] == username:
                user = User(
                    user_id=item["user_id"],
                    username=item["username"],
                    hashed_password=item["hashed_password"],
                    salt=item["salt"],
                    registration_date=datetime.fromisoformat(
                        item["registration_date"]
                    ),
                )

                if not user.verify_password(password):
                    raise ValueError("Неверный пароль")

                self.current_user = user

                return user.get_user_info()

        raise ValueError(f"Пользователь '{username}' не найден")
    
    def _load_portfolio(self):
        if self.current_user is None:
            raise ValueError("Сначала выполните login")

        portfolios = load_json("portfolios.json")

        for item in portfolios:
            if item["user_id"] == self.current_user.user_id:
                wallets = {}

                for code, wallet_data in item["wallets"].items():
                    wallets[code] = Wallet(
                        currency_code=code,
                        balance=wallet_data["balance"],
                    )

                return Portfolio(
                    user=self.current_user,
                    wallets=wallets,
                )

        raise ValueError("Портфель пользователя не найден")
    def show_portfolio(self, base_currency="USD"):
        portfolio = self._load_portfolio()

        if (
            not isinstance(base_currency, str)
            or not base_currency.strip()
        ):
            raise ValueError("Код валюты должен быть непустой строкой")

        base = base_currency.strip().upper()

        # get_rate уже умеет проверять, известна ли валюта.
        try:
            get_rate(base, base)
        except ValueError as error:
            raise ValueError(
                f"Неизвестная базовая валюта '{base}'"
            ) from error

        rows = []

        for code, wallet in portfolio.wallets.items():
            rate_info = get_rate(code, base)
            value = wallet.balance * rate_info["rate"]

            rows.append({
                "currency_code": code,
                "balance": wallet.balance,
                "value": value,
            })

        return {
            "username": portfolio.user.username,
            "base": base,
            "wallets": rows,
            "total": portfolio.get_total_value(base),
        }