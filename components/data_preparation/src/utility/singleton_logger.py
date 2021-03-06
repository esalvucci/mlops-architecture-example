from enum import Enum
import logging
from logging.handlers import RotatingFileHandler

component_name = "data_preparation"
log_format = '[%(asctime)s] - %(message)s'


class SingletonLogger(Enum):
    """
    Singleton implementation used to configure and get a python logger instance
    """
    @staticmethod
    def get_logger():
        # logger configuration
        logger = logging.getLogger(component_name)
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(component_name + '.log',
                                      maxBytes=100000,
                                      backupCount=5)
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        if logger.hasHandlers():
            logger.handlers.clear()
        logger.addHandler(handler)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger
