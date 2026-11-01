import hashlib # Разрешена по условию задачи
from valutatrade_hub.core.utils import get_rate

class User:
    # В рамках данного проекта оформление кода может
    # чуть отходить от строгил правил в пользу читаемости
    def __init__(self,
        user_id,
        username,
        password,
        salt,
        registration_date):
        self._user_id = user_id
        # вызываем метод, который проверят имя
        # и уже потом фиксирует его в памяти
        self.username = username 
        self._salt = salt
        # вызываем метод, который проверят пароль
        # хэширует его 
        # и уже потом фиксирует его в памяти
        self.change_password(password)
        self._registration_date = registration_date
    
    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Неверное имя пользователя")
        self._username = value.strip()

    @property
    def hashed_password(self):
        # Хранится именно хэшированный пароль
        return self._hashed_password

    @property
    def salt(self):
        return self._salt

    @property
    def registration_date(self):
        return self._registration_date

    def _hash_password(self, password):
        # encode() переводит строку в байты - нужно для работы с hashlib
        # hashlib.sha256 () вычисляет хэш этих байтов по указанному алгоритму
        # .hexdigest() - возвращает хэш в виде строку из 64 символов
        return hashlib.sha256((password + self.salt).encode()).hexdigest()
    
    def change_password(self, new_password: str):
        if not isinstance(new_password, str) or len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._hashed_password = self._hash_password(new_password)

    def get_user_info(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "registration_date": self.registration_date.isoformat(),
        }

    # -> bool означает ожидаемый тип на return
    def verify_password(self, password: str) -> bool:
        if not isinstance(password, str):
            return False
        return self.hashed_password == self._hash_password(password)

class Wallet:
    def __init__(
        self, 
        currency_code,
        balance = 0.0 #если юзер не введ баланс
        ):
        self.balance = balance
        self.currency_code = currency_code #не уверен

    @property
    def balance(self):
        return self._balance
    @balance.setter
    def balance(self, amount):
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Баланс должен быть неотрицательным числом")
        self._balance = amount
    def deposit(self, amount: float):
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Сумма депозита должна быть неотрицательным числом")
        self.balance += amount
    def withdraw(self, amount:float):
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Сумма снятия должна быть неотрицательным числом")
        if amount > self.balance:
            raise ValueError("Недостаточно средств")
        self.balance -= amount
    def get_balance_info(self):
        return {
            "currency_code": self.currency_code,
            "balance": self.balance,
        }
class Portfolio:
    def __init__(
        self,
        user,
        wallets=None
        ):
        self._user_id = user.user_id
        self._user = user
        self._wallets = {} if wallets is None else wallets.copy()

    @property
    def user(self):
        return self._user
    
    @property
    def wallets(self):
        return self._wallets.copy()

    def add_currency(self, currency_code):
        if not isinstance(currency_code, str) or not currency_code.strip():
            raise ValueError("Код валюты должен быть непустой строкой")
        code = currency_code.strip().upper()

        if code in self._wallets:
            raise ValueError(f"Кошелёк '{code}' уже существует")

        self._wallets[code] = Wallet(code)

    def get_wallet(self, currency_code):
        if not isinstance(currency_code, str) or not currency_code.strip():
            raise ValueError("Код валюты должен быть непустой строкой")
        code = currency_code.strip().upper()

        if code not in self._wallets:
            raise ValueError(f"У вас нет кошелька '{code}'")

        return self._wallets[code]

    def get_total_value(self, base_currency="USD"):
        if not isinstance(base_currency, str) or not base_currency.strip():
            raise ValueError("Код валюты должен быть непустой строкой")
        base = base_currency.strip().upper()
        total = 0.0
        for code, wallet in self._wallets.items():
            rate_info = get_rate(code, base)
            rate = rate_info["rate"]
            value = wallet.balance * rate
            # Суммируем стоимости
            total += value
        # Возвращаем общую стоимость
        return total