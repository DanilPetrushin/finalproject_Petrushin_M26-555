#https://metanit.com/python/tutorial/6.9.php - про secrets
# Не указан, как раз разрешённый, однако является
# встроенным и используется для подобных задач
import secrets  
from datetime import datetime, timezone
from valutatrade_hub.core.exceptions import InsufficientFundsError
from valutatrade_hub.core.models import Portfolio, User, Wallet
from valutatrade_hub.core.utils import (
    get_rate,
    load_json,
    normalize_currency,
    save_json,
    validate_amount,
)
from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.decorators import log_action
from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import InsufficientFundsError

class TradingService:
    def __init__(self):
        self.current_user = None
        # Пока никто не вошёл current_user = None
        self._settings = SettingsLoader()
    def register(self, username, password):
        users = load_json(self._settings.get("USERS_FILE"))

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
                    hashed_password="", 
                    salt = secrets.token_hex(8), 
                    registration_date = datetime.now(timezone.utc))
        user.change_password(password)
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
        portfolios = load_json(self._settings.get("PORTFOLIOS_FILE"))
        portfolios.append({
            "user_id": portfolio.user.user_id,
            "wallets": portfolio.wallets,
        })

        # Сохраняем переменные с данными в JSON
        save_json(self._settings.get("USERS_FILE"), users)
        save_json(self._settings.get("PORTFOLIOS_FILE"), portfolios)

        return user.get_user_info()
    
    def login(self, username, password):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Неверное имя пользователя")

        username = username.strip()

        users = load_json(self._settings.get("USERS_FILE"))

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
    def _save_portfolio(self, portfolio):
        portfolios = load_json(self._settings.get("PORTFOLIOS_FILE"))
        wallets_data = {}
        for code, wallet in portfolio.wallets.items():
            wallets_data[code] = {
                "balance": wallet.balance,
            }
        for item in portfolios:
            if item["user_id"] == portfolio.user.user_id:
                item["wallets"] = wallets_data
                save_json(self._settings.get("PORTFOLIOS_FILE"), portfolios)
                return
        raise ValueError("Портфель пользователя не найден")
    def _load_portfolio(self):
        # вот ради этого мы сделали класс
        if self.current_user is None:
            raise ValueError("Сначала выполните login")
    
        portfolios = load_json(self._settings.get("PORTFOLIOS_FILE"))
    
        for item in portfolios:
            if item["user_id"] == self.current_user.user_id:
                # 
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
    # разделил для простоты восприятия

    def show_portfolio(self, base_currency=None):
        # прежде base_currency указывалась как = USD, однако по условию
        # singleton должен указывать её, поэтому меняем на =None и если
        # пользователь не указал её, то ищем в settings.py
        # P.S. вообще здесь = None не обязателен, но лучше добавить, чем не добавлять
        from valutatrade_hub.core.currencies import get_currency
        portfolio = self._load_portfolio()
        if base_currency is None:
            base_currency = self._settings.get("DEFAULT_BASE_CURRENCY")

        base = get_currency(base_currency).code
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
    @log_action("BUY", verbose=True)
    def buy(self, currency_code, amount):
        portfolio = self._load_portfolio()
        # Приводим к общему виду входные данные + проверяем их
        code = get_currency(currency_code).code
        amount = validate_amount(amount)
        # Конечно, можно и без этого, но зачем покупать USD за USD?
        if code == "USD":
            raise ValueError("USD — расчётная валюта. Выберите другую валюту")
        # Получаем курс
        rate_info = get_rate(code, "USD")

        rate = rate_info["rate"]
        cost = validate_amount(amount * rate)

        if "USD" not in portfolio.wallets:
            raise InsufficientFundsError(available=0.0,required=cost,code="USD")

        usd_wallet = portfolio.get_wallet("USD")

        if code not in portfolio.wallets:
            portfolio.add_currency(code)

        wallet = portfolio.get_wallet(code)
        before = wallet.balance

        usd_wallet.withdraw(cost)
        wallet.deposit(amount)

        self._save_portfolio(portfolio)

        return {
            "currency_code": code,
            "amount": amount,
            "rate": rate,
            "cost": cost,
            "before": before,
            "after": wallet.balance,
        }
    @log_action("SELL", verbose=True)
    def sell(self, currency_code, amount):
        #Начало из buy()
        portfolio = self._load_portfolio()
        code = get_currency(currency_code).code
        amount = validate_amount(amount)
        if code == "USD":
            raise ValueError("USD — расчётная валюта. Выберите другую валюту")

        if code not in portfolio.wallets:
            raise InsufficientFundsError(available=0.0,required=amount,code=code)
        wallet = portfolio.get_wallet(code)

        if amount > wallet.balance:
            raise InsufficientFundsError(
                available=wallet.balance,
                required=amount,
                code=code,
            )

        rate_info = get_rate(code, "USD")

        rate = rate_info["rate"]
        cost = validate_amount(amount * rate)

        if "USD" not in portfolio.wallets:
            portfolio.add_currency("USD")

        usd_wallet = portfolio.get_wallet("USD")
        before = wallet.balance

        wallet.withdraw(amount)
        usd_wallet.deposit(cost)

        self._save_portfolio(portfolio)

        return {
            "currency_code": code,
            "amount": amount,
            "rate": rate,
            "cost": cost,
            "before": before,
            "after": wallet.balance,
        }
    def get_rate(self, from_currency, to_currency):
        source = normalize_currency(from_currency)
        target = normalize_currency(to_currency)

        result = get_rate(source, target)

        result["from_currency"] = source
        result["to_currency"] = target

        return result