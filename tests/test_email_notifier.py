import pytest
from unittest.mock import patch, mock_open, Mock, MagicMock
from psycopg.rows import dict_row
from datetime import date


from email_notifier.email_notifier_app import EmailNotifier


class TestEmailNotifier:

    @pytest.fixture
    def mock_db_connector(self):
        """
        Fixture to mock the DatabaseConnector.
        """
        with patch('email_notifier.email_notifier_app.DatabaseConnector') as mock_db_connector_class:
            mock_db_connector_instance = MagicMock()
            mock_db_connector_class.return_value = mock_db_connector_instance
            yield mock_db_connector_instance
    
    @pytest.fixture
    def mock_email_manager(self):
        """
        Fixture to mock the SendGridEmailManager.
        """
        with patch('email_notifier.email_notifier_app.SendGridEmailManager') as mock_email_manager_class:
            mock_email_manager_instance = MagicMock()
            mock_email_manager_class.return_value = mock_email_manager_instance
            yield mock_email_manager_instance
    
    @pytest.fixture
    def email_notifier(self, mock_db_connector, mock_email_manager):
        """
        Fixture to provide an EmailNotifier instance with mocked dependencies.
        """
        with patch('email_notifier.email_notifier_app.DatabaseConnector', return_value=mock_db_connector), \
            patch('email_notifier.email_notifier_app.SendGridEmailManager', return_value=mock_email_manager):
            notifier = EmailNotifier()
            yield notifier


    def test_fetch_upcoming_releases_with_days_ahead(self, email_notifier, mock_db_connector):
        """
        Test that fetch_upcoming_releases returns correct data when days_ahead is provided.
        """
        mock_db_connector.execute_query.return_value = [
            {'id': 1, 'manga_title': 'Manga A', 'volume_number': '1', 'release_date': '2023-10-01', 'publisher': 'Publisher A', 'page_link': 'http://example.com/manga-a'}
        ]

        releases = email_notifier.fetch_upcoming_releases(days_ahead=7)

        mock_db_connector.execute_query.assert_called_once()
        assert len(releases) == 1
        assert releases[0]['manga_title'] == 'Manga A'
    
    def test_fetch_upcoming_releases_no_days_ahead(self, email_notifier, mock_db_connector):
        """
        Test that fetch_upcoming_releases returns correct data when days_ahead is None.
        """
        mock_db_connector.execute_query.return_value = [
            {'id': 2, 'manga_title': 'Manga B', 'volume_number': '2', 'release_date': '2023-11-01', 'publisher': 'Publisher B', 'page_link': 'http://example.com/manga-b'}
        ]

        releases = email_notifier.fetch_upcoming_releases(days_ahead=None)

        mock_db_connector.execute_query.assert_called_once()
        assert len(releases) == 1
        assert releases[0]['manga_title'] == 'Manga B'
    
    def test_fetch_upcoming_releases_exception(self, email_notifier, mock_db_connector):
        """
        Test that fetch_upcoming_releases handles exceptions properly.
        """
        mock_db_connector.execute_query.side_effect = Exception('Database Error')

        with pytest.raises(Exception) as exc_info:
            email_notifier.fetch_upcoming_releases(days_ahead=7)

        assert 'Database Error' in str(exc_info.value)
    

    def test_fetch_subscribers_for_manga(self, email_notifier, mock_db_connector):
        """
        Test that fetch_subscribers_for_manga returns the correct data.
        """
        mock_db_connector.execute_query.return_value = [
            {'id': 1, 'email_address': 'user@example.com'}
        ]

        subscribers = email_notifier.fetch_subscribers_for_manga('Manga A')

        mock_db_connector.execute_query.assert_called_once()
        assert len(subscribers) == 1
        assert subscribers[0]['email_address'] == 'user@example.com'
    

    def test_fetch_subscribers_for_manga_exception(self, email_notifier, mock_db_connector):
        """
        Test that fetch_subscribers_for_manga handles exceptions properly.
        """
        mock_db_connector.execute_query.side_effect = Exception('Database Error')

        with pytest.raises(Exception) as exc_info:
            email_notifier.fetch_subscribers_for_manga('Manga A')

        assert 'Database Error' in str(exc_info.value)
    

    def test_mark_alert_sent(self, email_notifier, mock_db_connector):
        """
        Test that mark_alert_sent executes the correct query.
        """
        email_notifier.mark_alert_sent(manga_release_id=1, alert_type='1_week', email_address='user@example.com')

        mock_db_connector.execute_query.assert_called_once()
        called_args = mock_db_connector.execute_query.call_args
        assert 'INSERT INTO alerts_sent' in called_args[0][0]
        assert called_args[0][1] == [1, '1_week', 'user@example.com']

    
    def test_mark_alert_sent_exception(self, email_notifier, mock_db_connector):
        """
        Test that mark_alert_sent executes the correct query.
        """
        mock_db_connector.execute_query.side_effect = Exception('Database Error')

        with pytest.raises(Exception) as exc_info:
            email_notifier.mark_alert_sent(manga_release_id=1, alert_type='1_week', email_address='user@example.com')

        assert 'Database Error' in str(exc_info.value)
    

    def test_alert_already_sent_true(self, email_notifier, mock_db_connector):
        """
        Test that alert_already_sent returns True when alert has been sent.
        """
        mock_db_connector.execute_query.return_value = [{'alert_sent': True}]

        result = email_notifier.alert_already_sent(manga_release_id=1, alert_type='1_week', email_address='user@example.com')

        mock_db_connector.execute_query.assert_called_once()
        assert result is True


    def test_alert_already_sent_false(self, email_notifier, mock_db_connector):
        """
        Test that alert_already_sent returns False when alert has not been sent.
        """
        mock_db_connector.execute_query.return_value = [{'alert_sent': False}]

        result = email_notifier.alert_already_sent(manga_release_id=1, alert_type='1_week', email_address='user@example.com')

        mock_db_connector.execute_query.assert_called_once()
        assert result is False


    def test_alert_already_sent_exception(self, email_notifier, mock_db_connector):
        """
        Test that alert_already_sent returns True when an exception occurs (fails safe).
        """
        mock_db_connector.execute_query.side_effect = Exception('Database Error')

        result = email_notifier.alert_already_sent(manga_release_id=1, alert_type='1_week', email_address='user@example.com')

        mock_db_connector.execute_query.assert_called_once()
        assert result is True  


    def test_send_alerts(self, email_notifier, mock_db_connector, mock_email_manager):
        """
        Test that send_alerts sends emails and marks alerts as sent.
        """
        # Mock database responses
        # Set up side effects for execute_query calls
        def execute_query_side_effect(*args, **kwargs):
            query = args[0]
            if 'SELECT mr.id, mr.manga_title' in query:
                # fetch_upcoming_releases
                return [
                    {'id': 1, 'manga_title': 'Manga A', 'volume_number': '1', 'release_date': date.fromisoformat("2022-09-19"), 'publisher': 'Publisher A', 'page_link': 'http://example.com/manga-a'}
                ]
            
            elif 'SELECT s.email_address' in query:
                # fetch_subscribers_for_manga
                return [
                    {'email_address': 'user@example.com'}
                ]
            
            elif 'SELECT alert_sent' in query:
                # alert_already_sent
                return []  # No alert sent yet
            
            elif 'INSERT INTO alerts_sent' in query:
                # mark_alert_sent
                return None
            
            else:
                return []

        mock_db_connector.execute_query.side_effect = execute_query_side_effect

        mock_email_manager.send_email.return_value = None

        email_notifier.send_alerts()

        assert mock_email_manager.send_email.called
        assert mock_db_connector.execute_query.call_count >= 1



    









