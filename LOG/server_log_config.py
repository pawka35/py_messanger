'''
Определение параметров логирования сервера

'''

import logging
import logging.handlers
import os

# Папка где лежит настоящий файл
LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# Пусть до серверного лога
SERVER_LOG_FILE = os.path.join(LOG_FOLDER_PATH, 'server.log')

# Создаем именованный логгер с именем server
serverLogger = logging.getLogger('server')

# Создаем обработчик с ротацией файлом по дням
# сообщения будут выводиться в SERVER_LOF_FILE_PATH
serverHandler = logging.handlers.TimedRotatingFileHandler(SERVER_LOG_FILE, when='d', encoding='utf-8')
# serverHandler.setLevel(logging.DEBUG)

# Определяем Форматтер сообщения
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
formatter = logging.Formatter("%(asctime)s - %(levelname)s -  %(message)s")

# Связываем обработчик с форматером
serverHandler.setFormatter(formatter)

# Связываем логгер с обработчиком
serverLogger.addHandler(serverHandler)

# Устанавливаем уровень сообщений логгера
serverLogger.setLevel(logging.DEBUG)
