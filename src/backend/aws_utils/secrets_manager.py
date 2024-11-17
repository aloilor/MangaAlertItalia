import boto3
import json
import logging
import os
import base64


logger = logging.getLogger(__name__)

class AWSSecretsManagerClient:
    """
    A client to interact with AWS Secrets Manager.
    """

    def __init__(self, region_name="eu-west-1"):
        """
        Initialize the Secrets Manager client.

        :param region_name: AWS region name. If None, uses the default region.
        """
        self.region_name = region_name
        self.session = boto3.session.Session()
        self.client = self.session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )
        logger.debug("AWSSecretsManagerClient initialized for region: %s", self.region_name)


    def get_secret(self, secret_name):
        """
        Retrieve a secret from AWS Secrets Manager.

        :param secret_name: The name of the secret.
        :return: The secret value as a dictionary.
        :raises Exception: If the secret cannot be retrieved.
        """
        try:
            logger.debug("Attempting to retrieve secret: %s", secret_name)
            response = self.client.get_secret_value(SecretId=secret_name)
            logger.debug("Successfully retrieved secret: %s", secret_name)
        except Exception as e:
            logger.error("Failed to retrieve secret '%s': %s", secret_name, e)
            raise Exception(f"Failed to retrieve secret '{secret_name}': {e}")

        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        else:
            # If secret is binary, decode it
            secret_binary = response['SecretBinary']
            decoded_binary_secret = base64.b64decode(secret_binary)
            return json.loads(decoded_binary_secret)

    
    def load_secret_as_env_vars(self, secret_name):
        """
        Retrieve a secret and set its contents as environment variables
        with names in the format 'SECRETNAME_key'.

        :param secret_name: The name of the secret.
        :raises Exception: If the secret cannot be retrieved or set as environment variables.
        """
        try:
            secret_dict = self.get_secret(secret_name)
            if isinstance(secret_dict, dict):
                for key, value in secret_dict.items():
                    env_var_name = f"{secret_name}_{key}"
                    os.environ[env_var_name] = value
                    logger.debug("Set environment variable %s", env_var_name)
                logger.info("All secret values have been set as environment variables with prefix '%s_'", secret_name)

            else:
                logger.error("Secret retrieved is not a dictionary.")
                raise Exception("Secret format is invalid; expected a JSON object.")
            
        except Exception as e:
            logger.error("Failed to load secret '%s' as environment variables: %s", secret_name, e)
            raise Exception(f"Failed to load secret '{secret_name}' as environment variables: {e}")

