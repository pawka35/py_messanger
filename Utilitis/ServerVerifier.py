'''
Метакласс ServerVerifier, выполняющий базовую проверку класса «Сервер»:
a) отсутствие вызовов connect для сокетов;
b) использование сокетов для работы по TCP.
'''


class ServerVerifier(type):
    """Метакласс для базовых проверок"""
    def __init__(self, clsname, bases, clsdict):
        for x in clsdict:
            if str(type(clsdict[x])) == "<class 'function'>":  # ищем запрещенку в функция класса
                allcalls = (clsdict[x].__code__.co_names)
                if 'connect' in allcalls:
                    print(f'В функции {clsdict[x]} вызываетя CONNECT, что запрещено нашими правилами!')
                if 'SOCK_STREAM' in allcalls:
                    print(f"Все хорошо, мы используем tcp-сокеты в функции {clsdict[x]}")
        # Обязательно вызываем конструткор предка:
        super().__init__(clsname, bases, clsdict)