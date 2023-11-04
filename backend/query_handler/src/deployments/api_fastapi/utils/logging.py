# import logging
# import sys
# from loguru import logger
# from ..config import LogConfig

# logger.remove()
# logger.add(
#     sys.stderr,
#     enqueue=True,
#     backtrace=True,
#     colorize=True,
#     level=LogConfig.LOG_LEVEL,
#     format=LogConfig.FORMAT,
#     serialize=LogConfig.JSON_LOGS,
# )


# class InterceptHandler(logging.Handler):
#     def emit(self, record):
#         # Get corresponding Loguru level if it exists
#         try:
#             level = logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno

#         # Find caller from where originated the logged message
#         frame, depth = logging.currentframe(), 2
#         while frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1

#         logger.opt(depth=depth, exception=record.exc_info).log(
#             level, record.getMessage()
#         )


# def setup_logger():
#     logging.root.handlers = [InterceptHandler()]
#     logging.root.setLevel(LogConfig.LOG_LEVEL)
