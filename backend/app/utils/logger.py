"""
This module defines a logger configuration for the application.

It defines a class AppLogger which contains a class method `get_logger`
that configures and returns a logger with a name defined as a class variable.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import logging
import sys
import traceback
from typing import Any

from tenacity import Future, RetryCallState


class AppLogger:
    """AppLogger class contains methods related to application's logging configuration."""

    _logger_name = "app"
    logger: logging.Logger = logging.getLogger(_logger_name)

    @classmethod
    def set_log_level(cls, log_level: int | str) -> None:
        """
        Set the log level of the existing logger and its handlers.

        Args:
            log_level (int): The desired log level.
        """
        cls.logger.setLevel(log_level)
        for handler in cls.logger.handlers:
            handler.setLevel(log_level)

    @classmethod
    def initialize_logger(cls, log_level: int = logging.DEBUG) -> None:
        """
        Initializes the logger with given log level and default configuration.

        Args:
            log_level (int): The desired log level. Defaults to logging.DEBUG.
        """
        # Remove any existing handlers.
        for item in cls.logger.handlers[:]:
            cls.logger.removeHandler(item)

        # Create new handler, targeting docker logs, sending to the console.
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        cls.logger.addHandler(handler)

        # Set the log level of the logger and its handlers.
        cls.set_log_level(log_level)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Retrieves the logger.

        If the logger doesn't have any handlers, it initializes it with default configuration.
        If the logger was configured externally, it simply retrieves it without modification.

        Return:
            logging.Logger: Configured logger with the name specified in the class variable.
        """
        if not cls.logger.hasHandlers():
            cls.initialize_logger()

        return cls.logger

    @classmethod
    def debug(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a debug message.

        If the logger has not been initialized, it initializes it.

        Args:
            message (str): The message to log.
            *args: Additional arguments to the message.
            **kwargs: Additional keyword arguments to the message.
        """
        cls.get_logger()
        if cls.logger.isEnabledFor(logging.DEBUG):
            cls.logger.debug(message, *args, **kwargs)

    @classmethod
    def info(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a info message.

        If the logger has not been initialized, it initializes it.

        Args:
            message (str): The message to log.
            *args: Additional arguments to the message.
            **kwargs: Additional keyword arguments to the message.
        """
        cls.get_logger()
        if cls.logger.isEnabledFor(logging.INFO):
            cls.logger.info(message, *args, **kwargs)

    @classmethod
    def warning(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a warning message.

        If the logger has not been initialized, it initializes it.

        Args:
            message (str): The message to log.
            *args: Additional arguments to the message.
            **kwargs: Additional keyword arguments to the message.
        """
        cls.get_logger()
        if cls.logger.isEnabledFor(logging.WARNING):
            cls.logger.warning(message, *args, **kwargs)

    @classmethod
    def exception(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a exception message.

        If the logger has not been initialized, it initializes it.

        Args:
            message (str): The message to log.
            *args: Additional arguments to the message.
            **kwargs: Additional keyword arguments to the message.
        """
        cls.get_logger()
        if cls.logger.isEnabledFor(logging.ERROR):
            cls.logger.exception(message, *args, **kwargs)

    @classmethod
    def error(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a error message.

        If the logger has not been initialized, it initializes it.

        Args:
            message (str): The message to log.
            *args: Additional arguments to the message.
            **kwargs: Additional keyword arguments to the message.
        """
        cls.get_logger()
        if cls.logger.isEnabledFor(logging.ERROR):
            cls.logger.error(message, *args, **kwargs)

    @classmethod
    def log_retry_attempt(cls, retry_state: RetryCallState) -> None:
        """
        Log retry attempt and the exception information.

        Args:
            retry_state (RetryCallState): The state of the retry attempt.
        """
        # Initializing the log message with the current retry attempt number
        log_msg: str = f"Retrying for {retry_state.attempt_number} "

        # Getting the outcome of the current attempt
        outcome: Future = retry_state.outcome

        # Ensure outcome is not None and has an exception
        if outcome and outcome.exception():
            # Extracting the exception (if any) from the outcome
            exception: BaseException | None = outcome.exception()  # type: ignore

            # Ensure we have a traceback before appending it to the message
            if exception:
                # Adding the exception details to the log message
                log_msg += f"time(s) due to: {str(exception)}"  # type: ignore

                # Formatting the traceback and adding it to the log message
                log_msg += "\n" + "".join(traceback.format_exception(exception))
        else:
            log_msg += "time(s). No exception captured."

        # Sending the log message to the logger with a level of debug
        cls.debug(log_msg)
