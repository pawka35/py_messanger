'''
Метакласс ClientVerifier, выполняющий базовую проверку класса «Клиент»:
a) отсутствие вызовов accept и listen для сокетов;
b) использование сокетов для работы по TCP;
c) отсутствие создания сокетов на уровне классов.
'''


class ClientVerifier(type):
    """Метакласс для базовой проверки класса Клиент"""
    def __init__(self, clsname, bases, clsdict):
        for x in clsdict:
            if str(type(clsdict[x])) != "<class 'function'>":  # ищем вызовы сокетов вне функций класса
                if "socket" in str(clsdict[x]):
                    print("Кто-то инициализировал сокет вне функции класса!")
                    print(clsdict[x])

        for x in clsdict:
            if str(type(clsdict[x])) == "<class 'function'>":  # ищем запрещенку в функция класса
                allcalls = (clsdict[x].__code__.co_names)
                if 'accept' in allcalls:
                    print(f'В функции {clsdict[x]} вызываетя ACCEPT, что запрещено нашими правилами!')
                if 'listen' in allcalls:
                    print(f'В функции {clsdict[x]} вызываетя LISTEN, что запрещено нашими правилами!')
                if 'SOCK_STREAM' in allcalls:
                    print(f"Все хорошо, мы используем tcp-сокеты в функции {clsdict[x]}")

        # Обязательно вызываем конструткор предка:
        super().__init__(clsname, bases, clsdict)