'''
unit тесты модуля utils
'''

import socket
import unittest
import json
from .utils import dict_to_bytes, bytes_to_dict, get_message, send_message


class TestEncodeDecode(unittest.TestCase):
    def test_dict_to_bytes(self):
        with self.assertRaises(TypeError):
            dict_to_bytes('abc')
        self.assertEqual(dict_to_bytes({'test': 'test'}), b'{"test": "test"}')

    def test_bytes_to_dict(self):
        with self.assertRaises(TypeError):
            bytes_to_dict(100)
        with self.assertRaises(TypeError):
            bytes_to_dict(b'["abc"]')
        self.assertEqual(bytes_to_dict(b'{"test": "test"}'), {'test': 'test'})


# Класс заглушка для сокета
class ClientSocket():
    """Класс-заглушка для операций с сокетом"""

    def __init__(self, sock_type=socket.AF_INET, sock_family=socket.SOCK_STREAM):
        pass

    def recv(self, n):
        # Наш класс заглушка будет всегда отправлять одинаковый ответ при вызов sock.recv
        message = {'response': 200}
        jmessage = json.dumps(message)
        bmessage = jmessage.encode('utf-8')
        return bmessage

    def send(self, bmessage):
        # можно переопределить метод send просто pass
        pass


class TestSendGet(unittest.TestCase):
    def test_get_mes(self):
        # подменяем настоящий сокет нашим классом заглушкой
        sock = ClientSocket()
        # теперь можем протестировать работу метода
        self.assertEqual(get_message(sock), {'response': 200})

    def test_send_mes(self):
        # подменяем настоящий сокет нашим классом заглушкой
        # зоздаем сокет, он уже был подменен
        sock = ClientSocket()
        # т.к. возвращаемого значения нету, можно просто проверить, что метод отрабатывает без ошибок
        self.assert_(send_message(sock, {'test': 'test'}) is None)
        # и проверяем, чтобы обязательно передавали словарь на всякий пожарный
        with self.assertRaises(TypeError):
            send_message(sock, 'test')


if __name__ == "__main__":
    unittest.main()


