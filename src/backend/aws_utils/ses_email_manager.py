import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class SESEmailManager:
    """
    A class to send emails using AWS SES.
    """

    def __init__(self, sender_email='no-reply@mangaalertitalia.it', region_name='eu-west-1'):
        """
        Initialize the EmailManager.

        :param region_name: AWS region where SES is configured.
        :param sender_email: Verified sender email address.
        """
        self.ses_client = boto3.client('ses', region_name=region_name)
        self.sender_email = sender_email
        logger.debug("EmailNotifier initialized with sender: %s, region: %s", self.sender_email, region_name)


    def send_email(self, recipient_email, subject, body_text, body_html=None):
        """
        Send an email to a recipient.

        :param recipient_email: Recipient's email address.
        :param subject: Email subject.
        :param body_text: Plain text email body.
        :param body_html: HTML email body (optional).
        """
        try:
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'}
                }
            }

            if body_html:
                message['Body']['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}

            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [recipient_email]},
                Message=message
            )
            logger.info("Email sent to %s with Message ID: %s", recipient_email, response['MessageId'])

        except ClientError as e:
            logger.error("Failed to send email to %s: %s", recipient_email, e.response['Error']['Message'])
            raise
