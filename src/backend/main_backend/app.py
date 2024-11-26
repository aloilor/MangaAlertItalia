from flask import Flask, request, jsonify
from aws_utils.db_connector import DatabaseConnector
from common_utils.logging_config import setup_logging

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


# Initialize the DatabaseConnector
db_connector = DatabaseConnector()

def check_subscriber_limit():
    """
    Checks if the subscribers table has less than max_subscribers records.
    Returns True if a new subscriber can be added, False otherwise.
    """
    try:
        db_connector.connect()
        count_query = "SELECT COUNT(*) FROM subscribers;"
        result = db_connector.execute_query(count_query)
        print(result)
        subscriber_count = result[0]['count']
        if subscriber_count < max_subscribers:
            return True
        else:
            return False

    except Exception as e:
        logger.error("Error checking subscriber limit: %s", e)
        # For safety, prevent adding more subscribers if there's an error
        return False

    finally:
        db_connector.close()


@app.route('/subscribe', methods=['POST'])
def subscribe():
    """
    Endpoint to handle user subscriptions.
    Expects JSON data with 'email' and 'subscriptions'.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    email = data.get('email')
    subscriptions = data.get('subscriptions')
    for manga_title in subscriptions:
        if manga_title not in authorized_mangas:
            return jsonify({'error': 'You provided a manga that is not yet supported, retry'}), 400

    if not email or not subscriptions:
        return jsonify({'error': 'Email and subscriptions are required'}), 400

    # Check if the subscriber limit has been reached
    if not check_subscriber_limit():
        return jsonify({'error': 'Subscriber limit reached. No more subscriptions are allowed at this time.'}), 403

    try:
        db_connector.connect()

        # Insert the subscriber into the 'subscribers' table
        insert_subscriber_query = """
            INSERT INTO subscribers (email_address)
            VALUES (%s)
            ON CONFLICT (email_address) DO NOTHING
            RETURNING id;
        """
        subscriber_result = db_connector.execute_query(insert_subscriber_query, (email,))
        if subscriber_result:
            subscriber_id = subscriber_result[0]['id']

        else:
            # Fetch the subscriber ID if it already exists and it hasn't been returned previously
            get_subscriber_query = "SELECT id FROM subscribers WHERE email_address = %s;"
            subscriber_result = db_connector.execute_query(get_subscriber_query, (email,))
            subscriber_id = subscriber_result[0]['id']

        # Insert subscriptions into 'subscribers_subscriptions' table
        for manga_title in subscriptions:
            insert_subscription_query = """
                INSERT INTO subscribers_subscriptions (subscriber_id, email_address, manga_title)
                VALUES (%s, %s, %s)
                ON CONFLICT (subscriber_id, manga_title) DO NOTHING;
            """
            db_connector.execute_query(insert_subscription_query, (subscriber_id, email, manga_title))
            
        logger.info(f"Succesful subscription for '{email}' for the following mangas: {subscriptions}")
        return jsonify({'message': 'Subscription successful'}), 200

    except Exception as e:
        logger.error("Error in subscription: %s", e)
        return jsonify({'error': 'An error occurred during subscription'}), 500

    finally:
        db_connector.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    