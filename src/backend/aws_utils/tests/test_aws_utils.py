import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open, Mock

from aws_utils.secrets_manager import AWSSecretsManagerClient


# Test data
SECRET_NAME = "my-secret"
SECRET_STRING = '{"username": "admin", "password": "secret"}'
SECRET_BINARY = b'\xDE\xAD\xBE\xEF'


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


