from concurrent_log_handler import ConcurrentRotatingFileHandler
import logging


def setup_logger(name, level=logging.DEBUG):
    """Настройка базового логгера с выводом в файл и консоль с ротацией файла."""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )
    # 10 * 1024 * 1024 = 10 MB
    file_handler = ConcurrentRotatingFileHandler(
        "bot.log", maxBytes=10 * 1024 * 1024, backupCount=1
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
