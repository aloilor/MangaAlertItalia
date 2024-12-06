import os
import subprocess
import threading
import logging

from botocore.exceptions import ClientError
from aws_utils.secrets_manager import AWSSecretsManagerClient
from .logging_config import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

SECRET_NAME = 'ssl/api.mangaalertitalia.it'
REGION_NAME = 'eu-west-1'  # e.g., 'us-east-1'
DOMAIN_NAME = 'api.mangaalertitalia.it'

def get_ssl_certificate(secret_name, region_name):
    """
    Retrieve SSL certificate and private key from AWS Secrets Manager using AWSSecretsManagerClient.
    """
    logger.info(f"Retrieving SSL certificate and private key from Secrets Manager for secret '{secret_name}'")
    try:
        secrets_manager = AWSSecretsManagerClient(region_name=region_name)
        secret_dict = secrets_manager.get_secret(secret_name)

        certificate = secret_dict.get('certificate')
        private_key = secret_dict.get('private_key')

        if not certificate or not private_key:
            logger.error("Certificate or private key not found in secret")
            raise ValueError(f"Certificate or private key not found in secret: {secret_name}")

        logger.info("Successfully retrieved SSL certificate and private key")
        return certificate, private_key

    except ClientError as e:
        logger.error(f"ClientError when retrieving secret '{secret_name}': {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error when retrieving secret '{secret_name}': {e}")
        raise


def write_ssl_files(certificate, private_key):
    """
    Write the SSL certificate and private key to files.
    """
    logger.info("Writing SSL certificate and private key to files")
    try:
        domain_ssl_dir = f'/etc/ssl/{DOMAIN_NAME}'
        os.makedirs(domain_ssl_dir, exist_ok=True)

        cert_path = os.path.join(domain_ssl_dir, 'fullchain.pem')
        key_path = os.path.join(domain_ssl_dir, 'privkey.pem')

        with open(cert_path, 'w') as cert_file:
            cert_file.write(certificate)
        with open(key_path, 'w') as key_file:
            key_file.write(private_key)

        os.chmod(key_path, 0o600)
        logger.info(f"SSL files written to {domain_ssl_dir}")

        # Return paths for use in Nginx configuration
        return cert_path, key_path

    except Exception as e:
        logger.error(f"Error writing SSL files: {e}")
        raise


def configure_nginx(cert_path, key_path):
    """
    Configure Nginx using the template.
    """
    logger.info("Configuring Nginx")
    try:
        template_path = '/etc/nginx/conf.d/default.conf.template'
        config_path = '/etc/nginx/conf.d/default.conf'

        with open(template_path, 'r') as template_file:
            config = template_file.read()

        # Replace placeholders with actual values
        config = config.replace('{{DOMAIN_NAME}}', DOMAIN_NAME)
        # config = config.replace('/etc/ssl/{{DOMAIN_NAME}}/fullchain.pem', cert_path)
        # config = config.replace('/etc/ssl/{{DOMAIN_NAME}}/privkey.pem', key_path)

        with open(config_path, 'w') as config_file:
            config_file.write(config)

        logger.info(f"Nginx configuration written to {config_path}")

    except Exception as e:
        logger.error(f"Error configuring Nginx: {e}")
        raise


def start_services():
    """
    Start Nginx and the Flask application.
    """
    logger.info("Starting Nginx and Flask application")
    try:
        # Start Nginx in a separate thread
        def start_nginx():
            logger.info("Nginx started")
            subprocess.run(['nginx', '-g', 'daemon off;'])

        nginx_thread = threading.Thread(target=start_nginx)
        nginx_thread.start()

        # Start Gunicorn application 
        logger.info("Starting Gunicorn server")
        subprocess.run(['gunicorn', 'main_backend.app:app', '-b', '0.0.0.0:5000', '--workers=1', '--log-level=info'])


    except Exception as e:
        logger.error(f"Error starting services: {e}")
        raise


if __name__ == '__main__':
    try:
        certificate, private_key = get_ssl_certificate(SECRET_NAME, REGION_NAME)
        cert_path, key_path = write_ssl_files(certificate, private_key)
        configure_nginx(cert_path, key_path)
        start_services()

    except Exception as e:
        logger.exception(f"Application failed: {e}")
        exit(1)
