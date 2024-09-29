import psycopg2
from psycopg2.extras import RealDictCursor
from .secrets_manager import AWSSecretsManagerClient

class DatabaseConnector:
    """
    A connector for PostgreSQL databases using credentials from AWS Secrets Manager.
    """

    def __init__(self, secret_name, host="manga-alert-pgsql-db.c9oy46eeqq9b.eu-west-1.rds.amazonaws.com", dbname="manga_alert_pgsql_db", region_name="eu-west-1", port=5432):
        """
        Initialize the Database Connector.

        :param secret_name: The name of the secret in AWS Secrets Manager.
        :param region_name: AWS region name. If None, uses the default region.
        """
        self.secret_name = secret_name
        self.region_name = region_name
        self.host = host
        self.port = port
        self.dbname = dbname
        self.secrets_client = AWSSecretsManagerClient(region_name=self.region_name)
        self.connection = None

    def connect(self):
        """
        Establish a connection to the PostgreSQL database.

        :raises Exception: If the connection cannot be established.
        """
        try:
            credentials = self.secrets_client.get_secret(self.secret_name)
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.dbname,
                user=credentials['username'],
                password=credentials['password']
            )
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")

    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the results.

        :param query: The SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        :return: Query results as a list of dictionaries.
        :raises Exception: If the query fails to execute.
        """
        if not self.connection:
            self.connect()

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            else:
                self.connection.commit()
                return None

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
