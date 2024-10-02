import boto3
import json

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

    def get_secret(self, secret_name):
        """
        Retrieve a secret from AWS Secrets Manager.

        :param secret_name: The name of the secret.
        :return: The secret value as a dictionary.
        :raises Exception: If the secret cannot be retrieved.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
        except Exception as e:
            raise Exception(f"Failed to retrieve secret '{secret_name}': {e}")
        
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        else:
            # If secret is binary
            return response['SecretBinary']
