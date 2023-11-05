import os


class LogConfig:
    LOG_LEVEL: bool = str(os.environ.get("LOG_LEVEL"))
    FORMAT: str = str(os.environ.get("LOG_FORMAT"))
