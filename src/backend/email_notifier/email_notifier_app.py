import logging


from aws_utils.ses_email_manager import SESEmailManager
from aws_utils.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Module to handle alerting subscribers about upcoming manga releases.
    """

    def __init__(self):
        """
        Initialize the EmailNotifier task.

        :param db_connector: An instance of DatabaseConnector.
        :param email_notifier: An instance of SESEmailManager.
        """

        self.secret_name = "rds!db-4a66914f-6981-4530-b0ee-679115c8aa8a"
        self.db_connector = DatabaseConnector(self.secret_name)
        self.ses_email_manager = SESEmailManager()

        logger.debug("EmailNotifier initialized.")

    
    def fetch_upcoming_releases(self, days_ahead=7):
        """
        Fetch upcoming manga releases within the next 'days_ahead' days.

        :param days_ahead: Number of days ahead to check for releases.
        :return: List of upcoming manga releases.
        """

        try:
            # query = """
            #     SELECT mr.id, mr.manga_title, mr.volume_number, mr.release_date, mr.publisher
            #     FROM manga_releases mr
            #     WHERE mr.release_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL %s
            # """
            # params = [f'{days_ahead} days']

            query = """
                SELECT mr.id, mr.manga_title, mr.volume_number, mr.release_date, mr.publisher, mr.page_link
                FROM manga_releases mr
                WHERE mr.release_date > CURRENT_DATE 
            """
            params = []
            results = self.db_connector.execute_query(query, params)
            logger.debug("Fetched %d upcoming releases.", len(results))
            return results
        
        except Exception as e:
            logger.error("Error fetching upcoming releases: %s", e)
            raise

    
    def fetch_subscribers_for_manga(self, manga_title):
        """
        Fetch subscribers who have subscribed to a specific manga.

        :param manga_title: Title of the manga.
        :return: List of subscribers' email addresses.
        """

        try:
            query = """
                SELECT s.id, s.email_address
                FROM subscribers s
                JOIN subscribers_subscriptions ss ON s.id = ss.subscriber_id
                WHERE ss.manga_title = %s
            """
            params = [manga_title]
            results = self.db_connector.execute_query(query, params)
            logger.debug("Fetched %d subscribers for manga: %s", len(results), manga_title)
            return results
        
        except Exception as e:
            logger.error("Error fetching subscribers for manga '%s': %s", manga_title, e)
            raise
    

    def mark_alert_sent(self, subscriber_id, manga_release_id, alert_type):
        """
        Mark a specific alert as sent for a subscriber and manga release.

        :param subscriber_id: ID of the subscriber.
        :param manga_release_id: ID of the manga release.
        :param alert_type: Type of the alert (e.g., 'on_subscription', '1_month', '1_week', '1_day').
        """

        try:
            query = """
                INSERT INTO alerts_sent (subscriber_id, manga_release_id, alert_type, alert_sent)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (subscriber_id, manga_release_id, alert_type) DO UPDATE
                SET alert_sent = TRUE;
            """
            params = [subscriber_id, manga_release_id, alert_type]
            self.db_connector.execute_query(query, params)
            logger.info(
                "Marked alert '%s' as sent for subscriber_id: %s, manga_release_id: %s",
                alert_type, subscriber_id, manga_release_id
            )

        except Exception as e:
            logger.error(
                "Error marking alert '%s' as sent for subscriber_id '%s', manga_release_id '%s': %s",
                alert_type, subscriber_id, manga_release_id, e
            )
            raise
    

    def alert_already_sent(self, subscriber_id, manga_release_id, alert_type):
        """
        Check if an alert has already been sent to a subscriber for a manga release.

        :param subscriber_id: ID of the subscriber.
        :param manga_release_id: ID of the manga release.
        :param alert_type: Type of the alert (e.g., 'on_subscription', '1_month', '1_week', '1_day').
        :return: True if alert has been sent, False otherwise.
        """

        try:
            query = """
                SELECT alert_sent
                FROM alerts_sent
                WHERE subscriber_id = %s AND manga_release_id = %s AND alert_type = %s
            """
            params = [subscriber_id, manga_release_id, alert_type]
            result = self.db_connector.execute_query(query, params)
            if result and result[0]['alert_sent']:
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(
                "Error checking if alert '%s' has been sent for subscriber_id '%s', manga_release_id '%s': %s",
                alert_type, subscriber_id, manga_release_id, e
            )
            # For safety, assume the alert has been sent to prevent duplicate emails
            return True


    def send_alerts(self):
        """
        Send alerts to subscribers for upcoming manga releases based on alert schedule.
        """
        try:
            # Define alert schedules
            alert_schedules = [
                {'alert_type': '1_month', 'days_before': 30},
                {'alert_type': '1_week', 'days_before': 7},
                {'alert_type': '1_day', 'days_before': 1}
            ]

            for schedule in alert_schedules:
                alert_type = schedule['alert_type']
                days_before = schedule['days_before']

                upcoming_releases = self.fetch_upcoming_releases(days_ahead=days_before)

                print(upcoming_releases)

                for release in upcoming_releases:
                    manga_release_id = release['id']
                    manga_title = release['manga_title']
                    volume_number = release['volume_number']
                    release_date = release['release_date']
                    publisher = release['publisher']
                    link = release['page_link']

                    subscribers = self.fetch_subscribers_for_manga(manga_title)

                    print(subscribers)

                    for subscriber in subscribers:
                        subscriber_id = subscriber['id']
                        email_address = subscriber['email_address']

                        print(subscriber)

                        # Check if the alert has already been sent
                        if self.alert_already_sent(subscriber_id, manga_release_id, alert_type):
                            continue

                        # Prepare and send the email
                        subject = f"Prossima Uscita: {manga_title} Vol. {volume_number} tra {days_before} giorni"
                        body_text = f"""Ciao,

                        Il manga '{manga_title}' Vol. {volume_number} sarà disponibile il {release_date.strftime('%d/%m/%Y')}.

                        Casa editrice: {publisher}
                        Link per l'acquisto: {link}
                    

                        Grazie per aver utilizzato il nostro servizio.

                        Cordiali saluti,
                        Manga Alert Italia

                        Questo è un messaggio automatico, per favore non rispondere a questa email.
                        """

                        try:
                            self.ses_email_manager.send_email(
                                recipient_email=email_address,
                                subject=subject,
                                body_text=body_text
                            )
                            logger.info(
                                "Sent '%s' alert to %s for manga_release_id %s",
                                alert_type, email_address, manga_release_id
                            )
                            # Mark the alert as sent
                            self.mark_alert_sent(subscriber_id, manga_release_id, alert_type)

                        except Exception as e:
                            logger.error("Failed to send '%s' alert to %s: %s", alert_type, email_address, e)
                            continue

        except Exception as e:
            logger.error("Error in send_alerts: %s", e)
            raise

    

    def fetch_latest_manga_release(self, manga_title):
        """
        Fetch the latest manga release for a given manga title.

        :param manga_title: Title of the manga.
        :return: Manga release details.
        """
        try:
            query = """
                SELECT mr.id AS manga_release_id, mr.volume_number, mr.release_date, mr.publisher
                FROM manga_releases mr
                WHERE mr.manga_title = %s
                ORDER BY mr.release_date DESC
                LIMIT 1
            """
            params = [manga_title]
            result = self.db_connector.execute_query(query, params)
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.error("Error fetching latest manga release for manga '%s': %s", manga_title, e)
            raise



        