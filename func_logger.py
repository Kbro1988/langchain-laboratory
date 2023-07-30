import logging
from typing import Union

'''
Add to modules with functions to log:

from func_logger import configure_logging, log_output

configure_logging(f"{__name__}-langchain.log")

@log_output
def func(x,y):
    return output

'''


def log_configure_map(level: str) -> Union[int, callable]:
    """
    Map a string representation of log level to the corresponding integer value.

    Parameters:
        level (str): The string representation of the log level.
            Possible values: 'debug', 'info', 'warning', 'error', 'critical'.

    Returns:
        int: The integer representation of the log level.

    Raises:
        ValueError: If the input 'level' is not a valid log level.
    """
    log_level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    if level.lower() not in log_level_map:
        raise ValueError(f"Invalid log level: '{level}'. Valid log levels are 'debug', 'info', 'warning', 'error', or 'critical'.")

    return log_level_map[level.lower()]


def log_output_map(level: str) -> Union[int, callable]:
    """
    Map a string representation of log level to the corresponding logging level object.

    Parameters:
        level (str): The string representation of the log level.
            Possible values: 'debug', 'info', 'warning', 'error', 'critical'.

    Returns:
        Union[int, callable]: The corresponding logging level object (int or callable).

    Raises:
        ValueError: If the input 'level' is not a valid log level.
    """
    log_level_map = {
        "debug": logging.debug,
        "info": logging.info,
        "warning": logging.warning,
        "error": logging.error,
        "critical": logging.critical,
    }

    if level.lower() not in log_level_map:
        raise ValueError(f"Invalid log level: '{level}'. Valid log levels are 'debug', 'info', 'warning', 'error', or 'critical'.")

    return log_level_map[level.lower()]


def configure_logging(log_filename: str = 'func_logger.log',
                      level: str = 'info') -> None:
    """
    Configures logging to log messages both to stdout (console) and a file in the current working directory.

    Parameters:
        log_filename (str, optional): The filename of the log file. Default is 'func_logger.log'.
        level (str, optional): Represents the log level used by logging. Default is 'info'.
            Possible log levels: 'debug', 'info', 'warning', 'error', 'critical'.
    """
    level = log_configure_map(level)

    # Configure the root logger
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create a handler to log to stdout (console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create a handler to log to a file in the CWD
    file_handler = logging.FileHandler(filename=log_filename)
    file_handler.setLevel(level)

    # Define the formatter for both handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers to the root logger
    logger = logging.getLogger('')
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def log_output(level='info'):
    """
    Decorator function that logs the output of the decorated function.

    Parameters:
        log_level (str, optional): The logging level for the log messages. Default is 'info'.

    Returns:
        function: The wrapped function.

    Returns a new function that acts as a wrapper around the original function
    to log the function call details before calling the original function.

    This decorator can be used to log the inputs and output of any function
    it decorates. It is particularly useful for monitoring and debugging purposes.
    The log messages will include the function name, input arguments, output,
    and the file path of the module where the function is defined.

    Example:
        @log_output(log_level=logging.WARNING)
        def divide_numbers(a, b):
            return a / b
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            """
            Wrapper function that logs the function call details and calls the original function.

            Parameters:
                *args: Positional arguments passed to the decorated function.
                **kwargs: Keyword arguments passed to the decorated function.

            Returns:
                Any: The return value of the decorated function.

            The wrapper function logs the function call detail after calling the original function.
            The log messages will be printed based on the provided log level.
            """
            log = log_output_map(level)
            result = func(*args, **kwargs)
            log(f"Function 'Function '{func.__name__}' called with arguments: {args}, {kwargs}. Output: {result}")
            return result
        return wrapper
    return decorator
