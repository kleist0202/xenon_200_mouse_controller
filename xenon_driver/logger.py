import logging
import logging.config


class CustomFormatter(logging.Formatter):

    grey = "\033[90m"
    green = "\033[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[91m"
    reset = "\x1b[0m"
    format = "%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'custom': {
            '()': CustomFormatter,
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'custom',
        }
    },
    'loggers': {
        '__main__': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['default']
    },
})

xenon_logger = logging.getLogger(__name__)
