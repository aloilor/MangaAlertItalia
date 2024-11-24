import os
import boto3
import logging
import json  # Import the json module
from certbot._internal import main as certbot_main
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    MAIN_DOMAIN_NAME = "api.mangaalertitalia.it"
    SECRET_NAME = "ssl/api.mangaalertitalia.it"
    DOMAIN_NAMES = [
        "api.mangaalertitalia.it",
        "www.api.mangaalertitalia.it"
    ]
    REGION_NAME = "eu-west-1"
    EMAIL = "aloisi.lorenzo99@gmail.com"

    # Create directories for Certbot
    os.makedirs('/tmp/etc/letsencrypt', exist_ok=True)
    os.makedirs('/tmp/var/lib/letsencrypt', exist_ok=True)
    os.makedirs('/tmp/var/log/letsencrypt', exist_ok=True)

    # Run Certbot to obtain the certificate
    certbot_args = [
        'certonly',
        '--non-interactive',
        '--agree-tos',
        '--email', EMAIL,
        '--dns-route53',
        '-d', DOMAIN_NAMES[0],
        '-d', DOMAIN_NAMES[1],
        '--config-dir', '/tmp/etc/letsencrypt',
        '--work-dir', '/tmp/var/lib/letsencrypt',
        '--logs-dir', '/tmp/var/log/letsencrypt',
        '--test-cert'
    ]

    try:
        certbot_main.main(certbot_args)

    except Exception as e:
        logger.error(f"Certbot failed: {e}")
        raise e

    # Read the certificate files
    cert_path = f'/tmp/etc/letsencrypt/live/{MAIN_DOMAIN_NAME}/fullchain.pem'
    key_path = f'/tmp/etc/letsencrypt/live/{MAIN_DOMAIN_NAME}/privkey.pem'

    with open(cert_path, 'r') as cert_file:
        certificate = cert_file.read()

    with open(key_path, 'r') as key_file:
        private_key = key_file.read()

    # Update AWS Secrets Manager
    client = boto3.client('secretsmanager', region_name=REGION_NAME)

    secret_value = {
        'certificate': certificate,
        'private_key': private_key
    }
    secret_string = json.dumps(secret_value)

    try:
        client.put_secret_value(
            SecretId=SECRET_NAME,
            SecretString=secret_string
        )
        logger.info(f"Successfully updated secret {SECRET_NAME}")
        
    except ClientError as e:
        logger.error(f"Error updating secret: {e}")
        raise e

    return {
        'statusCode': 200,
        'body': f"SSL certificate for {MAIN_DOMAIN_NAME} renewed and updated in Secrets Manager."
    }
