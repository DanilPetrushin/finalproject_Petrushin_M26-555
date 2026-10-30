import hashlib #Разрешена по условию задачи


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

 