import logging
import os


def setup_logger(name):
    """Настройка логгера с записью в файл"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Создаем папку logs, если её нет
    os.makedirs('logs', exist_ok=True)

    # Настройка вывода в файл
    file_handler = logging.FileHandler(f'logs/{name}.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger  # Важно: возвращаем объект логгера