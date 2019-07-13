'''
Здест лежат ключи протокола обмена между клиентов и сервером
представленые перечислениями
'''

from enum import Enum


# Ключи
# тип сообщения между клиентом и сервером
class PacketType(Enum):
    ACTION = 'action'
    TIME = 'time'  # время запроса
    USER = 'user'  # данные о пользователе - клиенте (вложенный словарь)
    ACCOUNT_NAME = 'account_name'  # имя пользователя - чата
    RESPONSE = 'response'  # код ответа
    ERROR = 'error'  # текст ошибки
    PASSWORD = 'password'  # пароль клиента

# Значения
class Actions(Enum):
    PRESENCE = 'presence'  # присутствие
    PROBE = 'probe'  # проверка присутвия
    MESSAGE = 'message'  # сообщение
    QUIT = 'quit'  # отключение от сервера
    AUTHENTICATE = 'authenticate'  # авторизация на сервере
    JOIN = 'join'  # присоединение к чату
    LEAVE = 'leave'  # покидание чата
    GETCONTACT = 'get_contacts'
    INCLUDECONTACT = 'add_contact'
    EXCLUDECONTACT = 'del_contact'


class Helpers(Enum):
    FROM = 'from'
    TO = 'to'

class AnswerCodes(Enum):  # Коды ответов (будут дополняться)
    BASIC_NOTICE = 100  # базовое уведомление
    IMPORTANT_NOTICE = 101  # важное уведомление
    OK = 200  # OK
    CREATED = 201  # объект создан
    ACCEPTED = 202  # подтверждение.
    WRONG_REQUEST = 400  # неправильный запрос/json объект
    NOT_AUTHORISE = 401  # не авторизован;
    WRONG_LOGIN = 402  # неправильный логин/пароль;
    FORBIDDEN = 403  # пользователь заблокирован;
    NOT_FOUND = 404  # пользователь/чат отсутствует на сервере;
    CONFLICT = 409  # уже имеется подключение с указанным логином;
    GONE = 410  # адресат существует, но недоступен (offline)
    SERVER_ERROR = 500  # ошибка сервера


RESPONSE_CODES = tuple([x.value for x in AnswerCodes])


