from flask import Flask, request, jsonify
from flask_cors import CORS
from aws_utils.db_connector import DatabaseConnector
from aws_utils.ses_email_manager import SESEmailManager
from common_utils.sg_email_manager import SendGridEmailManager
from common_utils.logging_config import setup_logging

import textwrap
import logging

app = Flask(__name__)

logger = logging.getLogger(__name__)
setup_logging()

authorized_mangas = [
    "Solo Leveling",
    "Chainsaw Man",
    "Jujutsu Kaisen"
]

max_subscribers = 15

CORS(app, resources={
    r"/subscribe": {
        "origins": ["https://www.mangaalertitalia.it", "https://mangaalertitalia.it", "http://localhost:3000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
    }
})

# Initialize Database Connector
db_connector = DatabaseConnector()

# Initialize Email Manager
email_manager = SendGridEmailManager(sender_email='no-reply@mangaalertitalia.it', region_name='eu-west-1')


class SubscriptionService:
    """
    A service class responsible for subscription-related logic,
    including subscriber limit checks, existence checks, adding subscribers,
    and sending welcome emails.
    """

    def __init__(self, db_connector, email_manager, max_subscribers, authorized_mangas, logger):
        """
        Initialize the SubscriptionService.

        :param db_connector: An instance of DatabaseConnector for database operations.
        :param email_manager: An instance of SESEmailManager for sending emails.
        :param max_subscribers: Maximum number of subscribers allowed.
        :param authorized_mangas: List of authorized manga titles.
        :param logger: Logger instance.
        """
        self.db_connector = db_connector
        self.email_manager = email_manager
        self.max_subscribers = max_subscribers
        self.authorized_mangas = authorized_mangas
        self.logger = logger

    def is_subscriber_limit_reached(self):
        """
        Checks if the subscriber limit is reached or not.
        Returns True if limit reached (no more allowed), False otherwise.
        """
        try:
            self.db_connector.connect()
            count_query = "SELECT COUNT(*) FROM subscribers;"
            result = self.db_connector.execute_query(count_query)
            subscriber_count = result[0]['count']
            return subscriber_count >= self.max_subscribers
        except Exception as e:
            self.logger.error("Error checking subscriber limit: %s", e)
            # For safety, consider limit reached if an error occurs
            return True
        finally:
            self.db_connector.close()

    def is_subscriber_existing(self, email):
        """
        Checks if a subscriber with the given email already exists in the database.
        
        :param email: The subscriber's email address.
        :return: True if subscriber exists, False otherwise.
        """
        try:
            self.db_connector.connect()
            query = "SELECT id FROM subscribers WHERE email_address = %s;"
            result = self.db_connector.execute_query(query, (email,))
            return len(result) > 0
        except Exception as e:
            self.logger.error("Error checking subscriber existence: %s", e)
            # If error occurs, assume not existing to allow processing but handle carefully
            return False
        finally:
            self.db_connector.close()

    def add_subscriber(self, email, subscriptions):
        """
        Adds a new subscriber if not existing. If already existing, returns False.
        
        :param email: Subscriber's email.
        :param subscriptions: List of selected mangas.
        :return: True if newly added, False if subscriber already existed.
        """
        # Check if subscriber already exists
        if self.is_subscriber_existing(email):
            return False

        try:
            self.db_connector.connect()
            insert_subscriber_query = """
                INSERT INTO subscribers (email_address)
                VALUES (%s)
                ON CONFLICT (email_address) DO NOTHING
                RETURNING id;
            """
            subscriber_result = self.db_connector.execute_query(insert_subscriber_query, (email,))
            if subscriber_result:
                subscriber_id = subscriber_result[0]['id']
            else:
                # Fetch subscriber ID if already exists but not returned previously
                get_subscriber_query = "SELECT id FROM subscribers WHERE email_address = %s;"
                subscriber_result = self.db_connector.execute_query(get_subscriber_query, (email,))
                subscriber_id = subscriber_result[0]['id']

            # Insert subscriptions
            insert_subscription_query = """
                INSERT INTO subscribers_subscriptions (subscriber_id, email_address, manga_title)
                VALUES (%s, %s, %s)
                ON CONFLICT (subscriber_id, manga_title) DO NOTHING;
            """
            for manga_title in subscriptions:
                self.db_connector.execute_query(insert_subscription_query, (subscriber_id, email, manga_title))
            
            self.logger.info(f"Successful subscription for '{email}' for the following mangas: {subscriptions}")
            return True
        except Exception as e:
            self.logger.error("Error in adding subscriber: %s", e)
            raise
        finally:
            self.db_connector.close()

    def send_welcome_email(self, email, subscriptions):
        """
        Sends a welcome email in Italian to the newly subscribed user,
        listing the selected mangas.

        :param email: The subscriber's email.
        :param subscriptions: List of selected mangas.
        """
        subject = "Benvenuto/a su MangaAlertItalia!"
        # Convert the subscriptions list into a formatted string
        mangas_list = ", ".join(subscriptions)

        body_text = textwrap.dedent(f"""
            Ciao,

            Grazie per esserti iscritto/a a Manga Alert Italia!
            Le serie a cui ti sei iscritto/a sono: {mangas_list}

            Riceverai tre notifiche: 1 mese prima, 1 settimana prima e 1 giorno prima che uscirà un nuovo capitolo su queste serie.

            Buona lettura,
            Lo staff di Manga Alert Italia
            """)

        self.email_manager.send_email(
            recipient_email=email,
            subject=subject,
            body_text=body_text
        )



# Initialize the SubscriptionService
subscription_service = SubscriptionService(
    db_connector=db_connector,
    email_manager=email_manager,
    max_subscribers=max_subscribers,
    authorized_mangas=authorized_mangas,
    logger=logger
)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    """
    Endpoint to handle user subscriptions.
    Expects JSON data with 'email' and 'subscriptions'.
    """
    data = request.get_json()
    if not data:
        logger.error("No input provided")
        return jsonify({'error': 'Nessun input è stato inviato'}), 400

    email = data.get('email')
    subscriptions = data.get('subscriptions')

    for manga_title in subscriptions or []:
        if manga_title not in authorized_mangas:
            logger.error("Not authorized manga")
            return jsonify({'error': 'Hai inserito un manga non supportato, riprova.'}), 400

    if not email or not subscriptions:
        logger.error("No email or subscription provided")
        return jsonify({'error': 'Email e serie di manga sono obbligatorie.'}), 400

    # Check subscriber limit
    if subscription_service.is_subscriber_limit_reached():
        logger.error("Max number of subscription reached")
        return jsonify({'error': 'Limite di iscrizioni raggiunto. Non sono permesse altre iscrizioni al momento.'}), 403

    try:
        newly_subscribed = subscription_service.add_subscriber(email, subscriptions)
        if not newly_subscribed:
            logger.error("User already subscribed")
            return jsonify({'error': 'Sei già iscritto/a.'}), 400
        else:
            # Send welcome email
            subscription_service.send_welcome_email(email, subscriptions)
            logger.error("User {email} correctly subscribed")
            return jsonify({'message': 'Iscrizione avvenuta con successo.'}), 200

    except Exception as e:
        logger.error("Error in subscription process: %s", e)
        return jsonify({'error': 'Si è verificato un errore durante l\'iscrizione.'}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
