# Some WEB pages:
#    https://stackoverflow.com/questions/59120160/log-only-to-a-file-and-not-to-screen-for-logging-debug

import os
import sys
import logging
import pathlib
from logging.handlers import RotatingFileHandler

# Set a format which is simpler for console and file use
formaterForConsoleStr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formaterForLogFileStr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'

# -----------------------------------------------------------------------
# Define custom log level, FATAL. Code execution will be terminated
# aka exit from the Python when this called.
# -----------------------------------------------------------------------
FATAL = logging.CRITICAL + 1
logging.addLevelName(FATAL, 'FATAL')


def fatal(self, message, *args, **kws):
    if self.isEnabledFor(logging.FATAL):
        self.log(FATAL, message, *args, **kws)
        sys.exit()


class CustomConsoleHandlerFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    grey = "\33[90m"
    yellow = "\33[33m"
    red = "\33[91m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = formaterForConsoleStr

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
        FATAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomLogFileHandlerFormatter(logging.Formatter):
    format = formaterForLogFileStr

    FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format,
        FATAL: format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LevelFilter:

    def __init__(self, level):
        self._level = level

    def filter(self, log_record):
        return log_record.levelno == self._level


# -----------------------------------------------------------------------
# Configure Python logger
# Note:
#    DEBUG and higher level (INFO, WARNING, ERROR, CRITICAL) log messages
#    will be logged into the specified log file,
#    BUT the sepcified loglevel and higher log messages will be
#    put into the STDO/STDERR.
#
# Input:
#    toolname        :    string, e.g: "BAT", "OMtool", ect
#    caller_module   :    string, the name of the Python module from where the logger setup is called
#                         Note: this needs for setup the logger handler for the specific Python module,
#                               e.g.: bat_prepare.py, bat_vm_start.py, ect. This information will be
#                               visible in the log entry.
#    loglevel        :    the level of the logger, e.g: logging.INFO
#    logfile         :    the full path of the log file to be used
# Output:
#    logger_object   :    logger object
# -----------------------------------------------------------------------
def setup(toolname, caller_module, loglevel, logfile):
    # Extract the path of the given log file,
    # and create the folder for the log if does not exists.
    logDir = os.path.dirname(os.path.realpath(logfile))
    pathlib.Path(logDir).mkdir(parents=True, exist_ok=True)

    # Add custom log level
    logging.Logger.fatal = fatal

    # Setup handler for logging into a file, where ALL log messages will be saved
    # So DEBUG | INFO | ect
    # Note: It is important to set the log level of the "main" logger_object
    #       to DEBUG. Otherwise DEBUG messages will not be saved in the log file.
    logFileHandler = RotatingFileHandler(logfile, mode='a', maxBytes=5 * 1024 * 1024,
                                         backupCount=3, encoding=None, delay=0)
    logFileHandler.setFormatter(CustomLogFileHandlerFormatter())
    logFileHandler.setLevel(logging.DEBUG)

    # Define a Handler which writes INFO messages or higher to the sys.stderr
    # So DEBUG will not be printed into the STDO/STDERR.
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(loglevel)

    # Tell the handler to use this format
    consoleHandler.setFormatter(CustomConsoleHandlerFormatter())

    # Return with the handlers to be used
    logger_object = logging.getLogger(toolname + "-" + caller_module)
    # Note: It is important to set the loglevel of the "main" logger_object
    #       to DEBUG, for able to print/save the lowest configured log level,
    #       by any handler. Thus, if for example the log level for the "main"
    #       logger_object sets to INFO, the DEBUG log entries will NOT be logged/saved
    #       by the logFileHandler, while the loglevel of that sets to DEBUG.
    logger_object.setLevel(logging.DEBUG)

    # Cleanup the handlers first.
    # Note: The handlers might be configured already if for any reason the logger setup is called with the same given name
    #       e.g.: setup("BAT", "bat_vm_start.py", logger.INFO, "/tmp/logger.log"),
    #       so in this case the handlers must be removed first, otherwise duplicated printout will be seen in the
    #       console and log file.
    logger_object.handlers = []

    # Configure handlers for the logger object
    # Note: logFileHandler should not be set here, because that
    #       is already added to the BASIC setup
    loggerHandlers = [consoleHandler, logFileHandler]
    for loggerHandler in loggerHandlers:
        logger_object.removeHandler(loggerHandler)
        logger_object.addHandler(loggerHandler)

    # Print the path of the log file where logger dumps the log entries
    logger_object.info("Logger log file is: " + logfile)

    return logger_object

