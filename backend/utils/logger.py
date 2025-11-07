import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    # 创建一个日志记录器
    logger = logging.getLogger("smartagent")
    logger.setLevel(logging.INFO)

    # 创建一个 TimedRotatingFileHandler，并设置日志文件名
    log_filename = "logs/smartagent2.0.log"
    file_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=30)
    file_handler.suffix = "%Y-%m-%d-%H-%M-%S.log"
    file_handler.encoding = "utf-8"
    file_handler.setLevel(logging.INFO)

    # 创建一个控制台处理器，用于将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 定义日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 确保日志刷新
    for handler in logger.handlers:
        handler.flush()

    return logger

mylog = setup_logger()