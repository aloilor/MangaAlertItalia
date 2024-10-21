import pytest
from unittest.mock import patch, mock_open, Mock, MagicMock
from psycopg.rows import dict_row


from aws_utils.secrets_manager import AWSSecretsManagerClient
from aws_utils.db_connector import DatabaseConnector


SECRET_NAME = "my-secret"
SECRET_STRING = '{"username": "admin", "password": "secret"}'
SECRET_BINARY = b'\xDE\xAD\xBE\xEF'
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
            mock_client.get_secret_value.return_value = {'SecretBinary': SECRET_BINARY}
            mock_client_constructor.return_value = mock_client

            secrets_client = AWSSecretsManagerClient(region_name="eu-west-1")
            secret = secrets_client.get_secret(SECRET_NAME)

            assert secret == SECRET_BINARY
            mock_client.get_secret_value.assert_called_once_with(SecretId=SECRET_NAME)


    def test_get_secret_with_secret_binary(Self):
        
        # Mock the boto3 client and its get_secret_value method
        with patch('boto3.session.Session.client') as mock_client_constructor:

            mock_client = Mock()
            mock_client.get_secret_value.return_value = {'SecretBinary': SECRET_BINARY}
            mock_client_constructor.return_value = mock_client

            secrets_client = AWSSecretsManagerClient(region_name="eu-west-1")
            secret = secrets_client.get_secret(SECRET_NAME)

            assert secret == SECRET_BINARY
            mock_client.get_secret_value.assert_called_once_with(SecretId=SECRET_NAME)



    def test_get_secret_handle_exception(self):
        
        # Mock the boto3 client and its get_secret_value method to raise an exception
        with patch('boto3.session.Session.client') as mock_client_constructor:
            mock_client = Mock()
            mock_client.get_secret_value.side_effect = Exception("AWS Error")
            mock_client_constructor.return_value = mock_client

            secrets_client = AWSSecretsManagerClient(region_name="eu-west-1")

            with pytest.raises(Exception) as exc_info:
                secrets_client.get_secret(SECRET_NAME)

            assert f"Failed to retrieve secret '{SECRET_NAME}': AWS Error" == str(exc_info.value)
            mock_client.get_secret_value.assert_called_once_with(SecretId=SECRET_NAME)


class TestDatabaseConnector:

    @pytest.fixture
    def mock_secrets_manager(self):
        with patch('aws_utils.db_connector.AWSSecretsManagerClient') as MockSecretsManagerClient:
            mock_secrets_client = MockSecretsManagerClient.return_value
            mock_secrets_client.get_secret.return_value = MOCK_CREDENTIALS
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

            assert "Failed to connect to database: Failed to retrieve secret" in str(exc_info.value)

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


        