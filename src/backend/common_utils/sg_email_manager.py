import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from botocore.exceptions import ClientError
from aws_utils.secrets_manager import AWSSecretsManagerClient  


logger = logging.getLogger(__name__)

class SendGridEmailManager:
    """
    A class to send emails using SendGrid. Mimics the signature and behavior of the SESEmailManager class.
    """

    def __init__(self, sender_email='no-reply@mangaalertitalia.it', region_name='eu-west-1', secrets_manager_client=None):
        """
        Initialize the SendGridEmailManager.

        :param sender_email: Sender's email address.
        :param region_name: AWS region where the SendGrid API key is stored (via Secrets Manager).
        :param secrets_manager_client: Instance of AWSSecretsManagerClient to retrieve secrets. 
                                       If None, a new instance will be created automatically.
        """
        # Retrieve SendGrid API key from AWS Secrets Manager
        if secrets_manager_client is None:
            secrets_manager_client = AWSSecretsManagerClient(region_name=region_name)
        
        try:
            secret_dict = secrets_manager_client.get_secret("sendgrid-api-key")
            self.sendgrid_api_key = secret_dict["sendgrid-api-key"]
            logger.debug("Successfully retrieved SendGrid API key from Secrets Manager.")
        except ClientError as e:
            logger.error("Failed to retrieve the SendGrid API key from Secrets Manager: %s", e)
            raise

        self.sg_client = SendGridAPIClient(self.sendgrid_api_key)
        self.sender_email = sender_email
        logger.debug("SendGridEmailManager initialized with sender: %s", self.sender_email)

    def send_email(self, recipient_email, subject, body_text, body_html=None):
        """
        Send an email to a recipient using SendGrid.

        :param recipient_email: Recipient's email address.
        :param subject: Email subject.
        :param body_text: Plain text email body.
        :param body_html: HTML email body (optional).
        :raises Exception: If the email fails to send.
        """
        try:
            message = Mail(
                from_email=self.sender_email,
                to_emails=recipient_email,
                subject=subject,
                plain_text_content=body_text
            )

            # Optionally add HTML content
            if body_html:
                message.html_content = body_html

            response = self.sg_client.send(message)
            logger.info("Email sent to %s with status code: %s", recipient_email, response.status_code)

        except Exception as e:
            logger.error("Failed to send email to %s: %s", recipient_email, str(e))
            raise
