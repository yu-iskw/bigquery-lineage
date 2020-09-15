import logging


def get_logger():
    # Configure logging.
    logger = logging.getLogger()
    log_handler = logging.StreamHandler()
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    return logger
