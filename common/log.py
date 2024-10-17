import logging
from logging.handlers import TimedRotatingFileHandler
import os


class CustomFormatter(logging.Formatter):
    # 终端日志支持颜色输出:
    # https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    blue = "\x1b[34;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s')
# 默认会打印到控制台, 要打印到文件可以调用 init_logger 接口
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)


def set_log_level(level):
    logger.setLevel(level)


def log_to_file(file_path, level=logging.INFO):
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        logger.warning(
            'Folder [{}] does not exist, creating to dump logs'.format(file_dir))
        os.makedirs(file_dir)
    file_handler = TimedRotatingFileHandler(
        file_path, when='M', interval=1, backupCount=5, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
