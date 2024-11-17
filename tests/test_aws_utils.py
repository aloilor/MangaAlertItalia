import pytest
from unittest.mock import patch, mock_open, Mock, MagicMock
from psycopg.rows import dict_row
from botocore.exceptions import ClientError
import base64
import json
import os



from aws_utils.secrets_manager import AWSSecretsManagerClient
from aws_utils.db_connector import DatabaseConnector
from aws_utils.ses_email_manager import SESEmailManager



SECRET_NAME = "my-secret"
SECRET_STRING = '{"username": "admin", "password": "secret"}'
SECRET_BINARY_CONTENT = '{"username": "admin", "password": "secret"}'
SECRET_BINARY = base64.b64encode(SECRET_BINARY_CONTENT.encode('utf-8'))  # Base64-encoded bytes
HOST = "manga-alert-host-test"
DBNAME = "manga_alert_db_test"
REGION_NAME = "eu-west-1-test"
PORT = 5432
MOCK_CREDENTIALS = {
    'username': 'test_user',
    'password': 'test_password'
}


class TestSecretsManager:

    def test_get_secret_with_secret_string(self):
        # Mock the boto3 client and its get_secret_value method
        with patch('boto3.session.Session.client') as mock_client_constructor:
            mock_client = Mock()
            # Simulate AWS returning a secret string
            mock_client.get_secret_value.return_value = {'SecretString': SECRET_STRING}
            mock_client_constructor.return_value = mock_client

            secrets_client = AWSSecretsManagerClient(region_name=REGION_NAME)
            secret = secrets_client.get_secret(SECRET_NAME)

            expected_secret = json.loads(SECRET_STRING)
            assert secret == expected_secret
            mock_client.get_secret_value.assert_called_once_with(SecretId=SECRET_NAME)

    def test_get_secret_with_secret_binary(self):
        # Mock the boto3 client and its get_secret_value method
        with patch('boto3.session.Session.client') as mock_client_constructor:
            mock_client = Mock()
            # Simulate AWS returning a binary secret
            mock_client.get_secret_value.return_value = {'SecretBinary': SECRET_BINARY}
            mock_client_constructor.return_value = mock_client

            secrets_client = AWSSecretsManagerClient(region_name=REGION_NAME)
            secret = secrets_client.get_secret(SECRET_NAME)

            expected_secret = json.loads(SECRET_BINARY_CONTENT)
            assert secret == expected_secret
            mock_client.get_secret_value.assert_called_once_with(SecretId=SECRET_NAME)

    def test_get_secret_handle_exception(self):
        # Mock the boto3 client and its get_secret_value method to raise an exception
        with patch('boto3.session.Session.client') as mock_client_constructor:
            mock_client = Mock()
            mock_client.get_secret_value.side_effect = Exception("AWS Error")
            mock_client_constructor.return_value = mock_client

            secrets_client = AWSSecretsManagerClient(region_name=REGION_NAME)

            with pytest.raises(Exception) as exc_info:
                secrets_client.get_secret(SECRET_NAME)

            assert str(exc_info.value) == f"Failed to retrieve secret '{SECRET_NAME}': AWS Error"
            mock_client.get_secret_value.assert_called_once_with(SecretId=SECRET_NAME)


class TestDatabaseConnector:

    @pytest.fixture
    def mock_secrets_manager(self):
        with patch('aws_utils.db_connector.AWSSecretsManagerClient') as MockSecretsManagerClient:
            mock_secrets_client = MockSecretsManagerClient.return_value
            mock_secrets_client.get_secret.return_value = MOCK_CREDENTIALS
            
            env_var_db_username = f"{SECRET_NAME}_username"
            env_var_db_password = f"{SECRET_NAME}_password"
            os.environ[env_var_db_username] = "test_user"
            os.environ[env_var_db_password] = "test_password"
            
            yield mock_secrets_client

    @pytest.fixture
    def mock_psycopg_connect(self):
        with patch('psycopg.connect') as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            yield mock_connect, mock_connection


    def test_connect(self, mock_secrets_manager, mock_psycopg_connect):
        mock_connect, _ = mock_psycopg_connect

        db_connector = DatabaseConnector(
            secret_name=SECRET_NAME,
            host=HOST,
            dbname=DBNAME,
            region_name=REGION_NAME,
            port=PORT
        )

        db_connector.connect()

        mock_connect.assert_called_once_with(
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            user=MOCK_CREDENTIALS['username'],
            password=MOCK_CREDENTIALS['password'],
            row_factory=dict_row
        )

    def test_execute_query_with_results(self, mock_secrets_manager, mock_psycopg_connect):
        _, mock_connection = mock_psycopg_connect
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Set up the cursor to return a result
        mock_cursor.description = ['column1', 'column2']
        mock_cursor.fetchall.return_value = [{'column1': 'value1', 'column2': 'value2'}]

        db_connector = DatabaseConnector(
            secret_name=SECRET_NAME,
            host=HOST,
            dbname=DBNAME,
            region_name=REGION_NAME,
            port=PORT
        )
        db_connector.connect()

        query = "SELECT * FROM test_table;"
        result = db_connector.execute_query(query)

        mock_cursor.execute.assert_called_once_with(query, None, prepare=True)
        mock_cursor.fetchall.assert_called_once()
        assert result == [{'column1': 'value1', 'column2': 'value2'}]

    def test_execute_query_without_results(self, mock_secrets_manager, mock_psycopg_connect):
        _, mock_connection = mock_psycopg_connect
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Set up the cursor to simulate a non-select query
        mock_cursor.description = None

        db_connector = DatabaseConnector(
            secret_name=SECRET_NAME,
            host=HOST,
            dbname=DBNAME,
            region_name=REGION_NAME,
            port=PORT
        )
        db_connector.connect()

        query = "INSERT INTO test_table (column1) VALUES (%s);"
        params = ('value1',)
        result = db_connector.execute_query(query, params)

        mock_cursor.execute.assert_called_once_with(query, params, prepare=True)
        mock_connection.commit.assert_called_once()
        assert result is None

    def test_connect_exception(self):
        with patch('aws_utils.db_connector.AWSSecretsManagerClient') as MockSecretsManagerClient:
            mock_secrets_client = MockSecretsManagerClient.return_value
            mock_secrets_client.get_secret.side_effect = Exception("Failed to retrieve secret")

            db_connector = DatabaseConnector(
                secret_name=SECRET_NAME,
                host=HOST,
                dbname=DBNAME,
                region_name=REGION_NAME,
                port=PORT
            )

            with pytest.raises(Exception) as exc_info:
                db_connector.connect()

            assert "Failed to connect to database" in str(exc_info.value)

    def test_close_connection(self, mock_secrets_manager, mock_psycopg_connect):
        _, mock_connection = mock_psycopg_connect

        db_connector = DatabaseConnector(
            secret_name=SECRET_NAME,
            host=HOST,
            dbname=DBNAME,
            region_name=REGION_NAME,
            port=PORT
        )
        db_connector.connect()

        db_connector.close()
        
        mock_connection.close.assert_called_once()


class TestSESEmailManager:
    @pytest.fixture
    def ses_email_manager(self):
        """
        Fixture to create an instance of SESEmailManager with a mocked boto3 SES client.
        """
        with patch('aws_utils.ses_email_manager.boto3.client') as mock_boto_client:
            mock_ses_client = MagicMock()
            mock_boto_client.return_value = mock_ses_client
            manager = SESEmailManager(sender_email='sender@example.com', region_name='eu-west-1')
            yield manager, mock_ses_client


    def test_send_email_success(self, ses_email_manager):
        """
        Test that send_email successfully sends an email when SES does not raise an exception.
        """
        manager, mock_ses_client = ses_email_manager

        # Test data
        recipient_email = 'recipient@example.com'
        subject = 'Test Subject'
        body_text = 'This is a test email.'
        body_html = '<p>This is a test email.</p>'

        manager.send_email(recipient_email, subject, body_text, body_html)

        mock_ses_client.send_email.assert_called_once_with(
            Source='sender@example.com',
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                }
            }
        )
    

    def test_send_email_failure(self, ses_email_manager):
        """
        Test that send_email raises an exception when SES send_email fails.
        """
        manager, mock_ses_client = ses_email_manager

        # Mock SES send_email to raise ClientError
        error_response = {
            'Error': {
                'Code': 'MessageRejected',
                'Message': 'Email address is not verified.'
            }
        }
        mock_ses_client.send_email.side_effect = ClientError(error_response, 'send_email')

        # Test data
        recipient_email = 'unverified@example.com'
        subject = 'Test Subject'
        body_text = 'This is a test email.'

        with pytest.raises(ClientError) as exc_info:
            manager.send_email(recipient_email, subject, body_text)

        assert exc_info.value.response['Error']['Code'] == 'MessageRejected'
        assert exc_info.value.response['Error']['Message'] == 'Email address is not verified.'




        