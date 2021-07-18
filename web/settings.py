import os
import logging
from datetime import time
from dotenv import load_dotenv


load_dotenv()

DT_FORMAT = "%m:%d:%H:%M:%S"

FLASK_DEBUG = bool(int(os.environ.get("FLASK_DEBUG")))
FLASK_PORT = int(os.environ.get("FLASK_PORT"))

REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_HOST = os.environ.get("REDIS_HOST")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

LOGGING_NAME = "info.log"
LOGGING_DIR = os.path.join(PROJECT_ROOT, "logs")
LOGGING_PATH = os.path.join(LOGGING_DIR, LOGGING_NAME)
LOGGING_CONF = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        "f": {"format": "%(asctime)s %(name)s:%(lineno)5s %(levelname)s:%(message)s"}
    },
    handlers={
        "h": {
            "level": logging.INFO,
            "formatter": "f",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGGING_PATH,
            "when": "midnight",
            "atTime": time(0, 0),
            "interval": 1,
            "backupCount": 10,
        }
    },
    loggers={
        None: {
            "handlers": ["h"],
            "level": logging.INFO,
        }
    },
)

if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR)
