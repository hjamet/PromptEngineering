import logging
from logging.handlers import RotatingFileHandler
import os
import inspect


class Logger:
    """
    A custom logger class that sets up logging with both console and file handlers.
    Includes filename and line number in log messages.
    """

    def __init__(self, name, log_file="app.log", level=logging.DEBUG):
        """
        Initialize the logger with the given name and log file.

        Args:
            name (str): The name of the logger.
            log_file (str): The name of the log file.
            level (int): The logging level.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Create file handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, log_file), maxBytes=1024 * 1024, backupCount=5  # 1MB
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        Get the logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger

    def _log_with_context(self, level, message, *args, **kwargs):
        """
        Log a message with context information (filename and line number).
        """
        frame = inspect.currentframe().f_back.f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno

        log_method = getattr(self.logger, level)
        log_method(f"[{filename}:{lineno}] {message}", *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self._log_with_context("debug", message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log_with_context("info", message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log_with_context("warning", message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log_with_context("error", message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log_with_context("critical", message, *args, **kwargs)
