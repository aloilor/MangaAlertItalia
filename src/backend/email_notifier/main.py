import logging

from common_utils.logging_config import setup_logging
from email_notifier.email_notifier_app import EmailNotifier


logger = logging.getLogger(__name__)

def main():
    setup_logging()

    try:
        logger.info("Email notifier task started...")

        email_notifier = EmailNotifier()
        email_notifier.send_alerts()

    except Exception as e:
        logger.error("An error occurred in the main execution: %s", e)

    finally:
        email_notifier.db_connector.close()
        logger.info("Email notifier task finished...")


if __name__ == '__main__':
    main()
