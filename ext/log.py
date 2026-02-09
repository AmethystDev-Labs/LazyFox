import logging
import sys
from datetime import datetime

# ANSI 颜色码
class LogColors:
    RESET = "\033[0m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_RED = "\033[91;1m"

LEVEL_COLORS = {
    logging.DEBUG: LogColors.BLUE,
    logging.INFO: LogColors.GREEN,
    logging.WARNING: LogColors.YELLOW,
    logging.ERROR: LogColors.RED,
    logging.CRITICAL: LogColors.BOLD_RED,
}

class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = LEVEL_COLORS.get(record.levelno, "")
        reset = LogColors.RESET

        level = record.levelname
        timestamp = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        message = record.getMessage()

        return f"{color}[{level}] ({timestamp}) - {message}{reset}"

def setup_logger(name: str = "app", level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(ColorFormatter())

    logger.handlers.clear()
    logger.addHandler(handler)

    return logger
