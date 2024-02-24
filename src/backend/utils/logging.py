import logging
import logging.config
import os
import sys
from logging import Formatter, Logger, handlers

from constants.env import ENV, LOGGING_FOLDER, Environment

LOGGING_TO_FILE: bool = True
# LOGGING_TO_CONSOLE: bool = True if ENV == Environment.DEV.name else False
LOGGING_TO_CONSOLE: bool = False

# Unit for log rotation, D: day, M: minute, S: second, H: hour, W: week
LOGGING_WHEN: str = 'H'
# Interval for log rotation (based on the above unit), so here it's 12 hours
LOGGING_INTERVAL: int = 12
# Number of log files to keep, so when the interval is 12 hours and 28 files are kept, it's 14 days
LOGGING_RETENTION_PERIOD: int = 28
# Log file name pattern for rotation
LOG_FILE_PATTERN = "%Y.%m.%d.log"
# Minimum logging level, DEV environment is DEBUG, PROD environment is INFO
LOGGING_LEVEL: int = logging.DEBUG if ENV == Environment.DEV.name else logging.INFO
# Log entry format
LOGGING_FORMATTER: str = "[%(name)s][%(levelname)s]|%(asctime)s|process:%(process)d|%(module)s|%(filename)s|@%(lineno)d|%(message)s"


class DefaultLogger:

    @staticmethod
    def get_logger(name: str) -> Logger:
        """Get logger

        Args:
            name (str): Logger name
        """
        if not os.path.exists(LOGGING_FOLDER):
            os.makedirs(LOGGING_FOLDER, exist_ok=True)

        logger: Logger = logging.getLogger(name)
        logger.setLevel(LOGGING_LEVEL)
        formatter: Formatter = Formatter(LOGGING_FORMATTER)

        # Logging file config
        file_handler = handlers.TimedRotatingFileHandler(
            filename=os.path.join(LOGGING_FOLDER, 'default.log'),
            when=LOGGING_WHEN,
            interval=LOGGING_INTERVAL,
            backupCount=LOGGING_RETENTION_PERIOD)
        file_handler.suffix = LOG_FILE_PATTERN
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Logging to stdout config
        if LOGGING_TO_CONSOLE:
            stream_handler = logging.StreamHandler(sys.stderr)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger


class CategoryLogger:
    """
    Logger for specific categories, each category has its own logging file name
    """

    @staticmethod
    def get_logger(category: str, name: str) -> Logger:
        """Get logger

        Args:
            category (str): The category name
            name (str): Logger name
            write_to_default (bool): Whether to write to the default logger also
        """

        cat_logging_dir: str = os.path.join(LOGGING_FOLDER, 'categorized')
        if not os.path.exists(cat_logging_dir):
            os.makedirs(cat_logging_dir, exist_ok=True)

        logger: Logger = logging.getLogger(name)
        logger.setLevel(LOGGING_LEVEL)
        formatter: Formatter = Formatter(LOGGING_FORMATTER)

        # Logging file config
        file_handler = handlers.TimedRotatingFileHandler(
            filename=os.path.join(cat_logging_dir, f'{category}.log'),
            when=LOGGING_WHEN,
            interval=LOGGING_INTERVAL,
            backupCount=LOGGING_RETENTION_PERIOD)
        file_handler.suffix = LOG_FILE_PATTERN
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Logging to stdout config
        if LOGGING_TO_CONSOLE:
            stream_handler = logging.StreamHandler(sys.stderr)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger
