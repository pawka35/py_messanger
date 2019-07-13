'''
unit тесты модуля сервера
'''

import time
from server import presence_response
import unittest


class TestServer(unittest.TestCase):
    # нет ключа action
    def test_action_response(self):
        self.assertEqual(presence_response({'one': 'two', 'time': time.time()}), {'response': 400, 'error': 'Не верный запрос'})

    # ключ action имеет значение не presence
    def test_presence_response(self):
        self.assertEqual(presence_response({'action': 'test_action', 'time': 1000.10}), {'response': 400, 'error': 'Не верный запрос'})

    # нет ключа time
    def test_time_response(self):
        self.assertEqual(presence_response({'action': 'presence'}), {'response': 400, 'error': 'Не верный запрос'})

    # неправильное время
    def test_time_incorrect_response(self):
        self.assertEqual(presence_response({'action': 'presence', 'time': 'test_time'}), {'response': 400, 'error': 'Не верный запрос'})

    # всё в порядке
        self.assertEqual(presence_response({'action': 'presence', 'time': 1000.10}), {'response': 200})


if __name__ == "__main__":
    unittest.main()