import logging
import os

def setup_logging():
    logging_level = os.environ.get('LOGGING_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s '
    )
