'''
unit тесты модуля клиента
'''

import time
import unittest
import sys
sys.path.append('../')
from ClientCore.client import Client as client
from Utilitis.errors import *


# тестируем функцию формирования сообщения от клиента
class TestClientCreatePresence(unittest.TestCase):

    # action формируется корректно
    def test_create_presence_non(self):
        self.assertEqual(client.create_presence()['action'], "presence")

    # проверяем, что имя клиента записывается корректно, если мы его передаем
    def test_create_presence_param(self):
        self.assertEqual(client.create_presence('test_user_name')["user"]["account_name"], 'test_user_name')

    # берем разницу во времени
    def test_create_presence_time(self):
        self.assertTrue(abs(client.create_presence()['time'] - time.time()) < 0.1)

    # неверный тип аккаунта - число
    def test_create_presence_acc_int(self):
        with self.assertRaises(DigitName):
            client.create_presence(200)

    # неверный тип аккаунта - None
    def test_create_presence_acc_none(self):
        with self.assertRaises(OutOfUserName):
            client.create_presence(None)

    # имя только из чисел
    def test_create_presence_acc_DigitOnly(self):
        with self.assertRaises(DigitName):
            client.create_presence('123')

    # имя более 25 символов
    def test_create_presence_acc_toolong(self):
        with self.assertRaises(UsernameToLongError):
            client.create_presence('ПетяпетяпетяПетяпетяпетяПетяпетяпетя')


# тестируем функцию разбора ответа сервера
class TestClientTranslateMessage(unittest.TestCase):
    # неправильный тип
    def test_translate_message_inc_type(self):
        with self.assertRaises(TypeError):
            client.translate_message(100)

    # нету ключа response
    def test_translate_message_not_resp(self):
        with self.assertRaises(MandatoryKeyError):
            client.translate_message({'one': 'two'})

    # неверная длина кода ответа
    def test_translate_message_incor_resp_len(self):
        with self.assertRaises(ResponseCodeLenError):
            client.translate_message({'response': '5'})

    # неверный код ответа
    def test_translate_message_incor_resp(self):
        with self.assertRaises(ResponseCodeError):
            client.translate_message({'response': 700})

    # все правильно
    def test_translate_message_cor_resp(self):
        self.assertEqual(client.translate_message({'response': 200}), {'response': 200})


if __name__ == "__main__":
    unittest.main()










