"""
Logging configuration for Literattus frontend.
Configures loguru to write to stdout/stderr for CloudWatch.
"""

import sys
from loguru import logger

# Remove default handler
logger.remove()

# Add stdout handler for CloudWatch
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    colorize=False,  # Disable colors for CloudWatch
    serialize=False,  # Plain text format
)

# Add stderr handler for errors
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="ERROR",
    colorize=False,
    serialize=False,
)

# Also configure Python's logging to use loguru
import logging

class InterceptHandler(logging.Handler):
    """Intercept standard logging messages toward loguru."""
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Configure Django logging to use loguru
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

