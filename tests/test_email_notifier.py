import pytest
from unittest.mock import patch, mock_open, Mock, MagicMock
from psycopg.rows import dict_row


from email_notifier.email_notifier_app import EmailNotifier


class TestEmailNotifier:

    def test_fetch_upcoming_releases(self):
        return

