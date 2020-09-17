import logging


def get_logger(log_level=logging.INFO):
    # Configure logging.
    logger = logging.getLogger()
    log_handler = logging.StreamHandler()
    logger.addHandler(log_handler)
    logger.setLevel(log_level)
    return logger
