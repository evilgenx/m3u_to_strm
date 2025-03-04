import logging
from enum import Enum
from os import path

from PyQt6.QtCore import QObject, pyqtSignal


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class UISignalEmitter(QObject):
    """
    Signal emitter for UI updates.
    """

    log_signal = pyqtSignal(str)


class Logger(object):
    def __init__(self, name: str, log_level: LogLevel = LogLevel.DEBUG) -> None:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        self.log = logging.getLogger(name)
        self.log.setLevel(log_level.value)  # Use .value to get the int value from Enum
        self.ui_emitter = UISignalEmitter()

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(log_level.value)
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

        # create file handler
        logs_folder = "logs"
        if not path.exists(logs_folder):
            path.makedirs(logs_folder, exist_ok=True)
        fh = logging.FileHandler(path.join(logs_folder, f"{name}.log")) # Use f-string here
        fh.setFormatter(formatter)
        fh.setLevel(log_level.value)
        self.log.addHandler(fh)

    def write_to_log(self, msg: str) -> None:
        self.log.debug(msg)
        self.ui_emitter.log_signal.emit(msg)
