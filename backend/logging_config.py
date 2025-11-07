import logging
from logging.handlers import TimedRotatingFileHandler
from config import settings

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = TimedRotatingFileHandler(
        settings.LOG_FILE, 
        when='midnight', 
        interval=1, 
        backupCount=7
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)