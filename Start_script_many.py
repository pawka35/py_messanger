'''
Cкрипт, запускающий сервер и указанное количество клиентских приложений.
'''

from subprocess import Popen, CREATE_NEW_CONSOLE


def start():
    p_list = []

    while True:
        choise=input("1.Запустить сервер\n"
                     "2. Запустить клиентов\n"
                     "3. Закрыть все процессы \n")

        if choise == '1':
            p_list.append(Popen('python Server_start.py', creationflags=CREATE_NEW_CONSOLE))
            print('Сервер запущен')

        elif choise == '2':
            colvo = int(input('Сколько клиентов запустить?:\n'))
            for _ in range(colvo):
                # Запускаем клиентский скрипт и добавляем его в список процессов
                    p_list.append(Popen('python -i Client_Start.py', creationflags=CREATE_NEW_CONSOLE))
            print('Клиенты на чтение запущены')
        elif choise == '3':
            print('Открыто процессов {}'.format(len(p_list)))
            for p in p_list:
                print('Закрываю {}'.format(p))
                p.kill()
            p_list.clear()
            print('Все процессы закрыты. Завершаю работу')
            break


if __name__ == '__main__':
    start()
