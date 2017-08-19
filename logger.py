import logging


__author__ = "Evgeny Goncharov"


class Logger:
    def __init__(self, file_name):
        file_handler = logging.FileHandler(file_name, "a")
        file_handler.flush()
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%e %b %y %H:%M:%S"
        )
        file_handler.setFormatter(fmt=formatter)
        self.logger = logging.getLogger()
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    def info(self, msg):
        self.logger.info(msg=msg)

    def error(self, msg):
        self.logger.error(msg=msg)

    def critical(self, msg):
        self.logger.critical(msg=msg)
