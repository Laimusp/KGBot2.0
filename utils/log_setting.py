import logging
import os


class CustomFileHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        os.makedirs('logs', exist_ok=True)
        
    def emit(self, record: logging.LogRecord) -> None:
        with open(f'logs/log{record.levelno}.log', 'w+') as log_file:
            log_file.write(self.format(record))


def configure_logging():
    logger = logging.getLogger('plugins')
    logger.setLevel(logging.INFO)
    handler = CustomFileHandler()
    handler.setFormatter(logging.Formatter('%(name)s:%(asctime)s:%(message)s'))
    logger.addHandler(handler)
