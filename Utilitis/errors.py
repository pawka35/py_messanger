"""
Модуль содержащий ошибки и описывающий реакцию на них
"""
# Создаем собственные исключения


# исключение. когда имя пользователя слишком длинное - более 25 символов
class UsernameToLongError(Exception):
    """Исключение. когда имя пользователя слишком длинное - более 25 символов"""
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f'Имя пользователя {self.username} должно быть менее 26 символов'


class OutOfUserName(Exception):
    """Исключение. когда имя пользователя отстутствует"""
    def __str__(self):
        return f'Не передано имя пользователя'


class DigitName(UsernameToLongError):
    """Исключение. когда имя пользователя состоит только из чисел"""
    def __str__(self):
        return f'Имя пользователя {self.username} не должно состоять только из чисел'


# исключение. переданный код отсутствует среди стандартных кодов
class ResponseCodeError(Exception):
    """исключение. переданный код отсутствует среди стандартных кодов"""
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f'Неверный код ответа {self.code}'


# исключение. длина кода - не три символа
class ResponseCodeLenError(ResponseCodeError):
    """исключение. длина кода - не три символа"""
    def __str__(self):
        return f'Неверная длина кода {self.code}. Длина кода должна быть 3 символа.'


# исключение. отсутствует обязательный атрибут response
class MandatoryKeyError(Exception):
    """исключение. отсутствует обязательный атрибут response"""
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f'Не хватает обязательного атрибута {self.key}'


