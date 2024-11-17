import psycopg
from psycopg.rows import dict_row
from .secrets_manager import AWSSecretsManagerClient
import logging
import os


logger = logging.getLogger(__name__)

class DatabaseConnector:
    """
    A connector for PostgreSQL databases using credentials from AWS Secrets Manager.
    """

    def __init__(self, secret_name="rds!db-4a66914f-6981-4530-b0ee-679115c8aa8a", host="manga-alert-pgsql-db.c9oy46eeqq9b.eu-west-1.rds.amazonaws.com", dbname="manga_alert_pgsql_db", region_name="eu-west-1", port=5432):
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
        logger.debug("DatabaseConnector initialized with host: %s, dbname: %s, region: %s, port: %d", self.host, self.dbname, self.region_name, self.port)


    def connect(self):
        """
        Establish a connection to the PostgreSQL database.

        If the environment variables for username and password are already set,
        use them. Otherwise, retrieve them from AWS Secrets Manager.

        If the connection fails due to authentication error, refresh the credentials
        from AWS Secrets Manager (in case the secrets have  rotated) and retry once.

        :raises Exception: If the connection cannot be established.
        """
        env_var_db_username = f"{self.secret_name}_username"
        env_var_db_password = f"{self.secret_name}_password"

        # Attempt to get credentials from environment variables
        db_username = os.getenv(env_var_db_username)
        db_password = os.getenv(env_var_db_password)

        # If credentials are not set in environment variables, load them from Secrets Manager
        if not db_username or not db_password:
            logger.info("Credentials not found in environment variables. Loading from Secrets Manager.")
            self.secrets_client.load_secret_as_env_vars(self.secret_name)
            db_username = os.getenv(env_var_db_username)
            db_password = os.getenv(env_var_db_password)

        try:
            self.connection = psycopg.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=db_username,
                password=db_password,
                row_factory=dict_row
            )
            logger.debug("Successfully connected to the database: %s", self.dbname)

        except psycopg.OperationalError as e:
            # Check if the error is due to password authentication failure
            error_message = str(e).lower()
            if 'password authentication failed' in error_message or 'authentication failed' in error_message:
                logger.warning("Password authentication failed. Refreshing credentials from Secrets Manager and retrying.")
               
                # Refresh credentials from Secrets Manager
                self.secrets_client.load_secret_as_env_vars(self.secret_name)
                db_username = os.getenv(env_var_db_username)
                db_password = os.getenv(env_var_db_password)
                
                # Try to connect again
                try:
                    self.connection = psycopg.connect(
                        host=self.host,
                        port=self.port,
                        dbname=self.dbname,
                        user=db_username,
                        password=db_password,
                        row_factory=dict_row
                    )
                    logger.debug("Successfully connected to the database after refreshing credentials.")
                
                except Exception as e:
                    logger.error("Failed to connect to database after refreshing credentials: %s", e)
                    raise Exception(f"Failed to connect to database after refreshing credentials: {e}")
            
            else:
                logger.error("Failed to connect to database: %s", e)
                raise Exception(f"Failed to connect to database: {e}")

        except Exception as e:
            logger.error("Failed to connect to database: %s", e)
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
            logger.debug("No active database connection found. Attempting to connect...")
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                logger.debug("Executing query: %s with params: %s", query, params)
                cursor.execute(query, params, prepare=True)
                
                # Only populated if the query returns rows (SELECT)
                if cursor.description:
                    results = cursor.fetchall()
                    logger.debug("Query executed successfully, returning %d rows", len(results))
                    return results

                # Query doesn't produce a result set (INSERT, UPDATE, DELETE)
                else:
                    self.connection.commit()
                    logger.debug("Query executed successfully, no result set returned")
                    return None
                
        except Exception as e:
            logger.error("Failed to execute query: %s, error: %s", query, e)
            raise Exception(f"Failed to execute query: {e}")


    def close(self):
        """
        Close the database connection.
        """
        
        if self.connection:
            try:
                self.connection.close()
                logger.debug("Database connection closed successfully.")
            except Exception as e:
                logger.error("Failed to close the database connection: %s", e)
                raise Exception(f"Failed to close the database connection: {e}")
            finally:
                self.connection = None
