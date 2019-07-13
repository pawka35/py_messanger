'''
Класс-дескриптор для проверки, что значение положительно
'''


class NonNegative:

    def __set__(self, instance, value):
        """Проверка на положительное значение"""
        print(f"Check {value}")
        if value < 0:
            raise ValueError("Не может быть отрицательным")
        instance.__dict__[self.my_attr] = value

    def __set_name__(self, owner, my_attr):
        self.my_attr = my_attr

