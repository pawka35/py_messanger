'''
Определение параметров логирования клиента
'''


import logging
import logging.handlers
import os

# Папка где лежит настоящий файл
LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# путь до клиентского лога
CLIENT_LOG_FILE = os.path.join(LOG_FOLDER_PATH, 'client.log')

# # Создаем именованный логгер с именем client
clientLogger = logging.getLogger('client')
# устанавливаем уровень логгера
clientLogger.setLevel(logging.DEBUG)

# обработчик будет логгер, который пишет в файл
clientHandler = logging.FileHandler(CLIENT_LOG_FILE, encoding='utf-8')

clientHandler = logging.handlers.RotatingFileHandler(CLIENT_LOG_FILE, maxBytes=2097152, backupCount=3, encoding='utf-8',)
# задаем уровень обработчика

# настраиваем форматтер вывода
formatter = logging.Formatter("%(asctime)s - %(levelname)s -  %(message)s")
# связываем с форматером
clientHandler.setFormatter(formatter)

# связываем с обработчиком
clientLogger.addHandler(clientHandler)

