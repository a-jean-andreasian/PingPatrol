import os
import unittest
from unittest.mock import patch, mock_open
from src.services.reporter.tg import TelegramReporter


class TestTelegramReporter(unittest.TestCase):
    def setUp(self):
        # Backup original environment
        self.original_env = os.environ.copy()
        os.environ.clear()

        # Mock environment file content
        self.env_content = """TOKEN=test_token
telegram_chat_id=test_chat_id
OTHER_VAR=test_value
"""

    def tearDown(self):
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('builtins.open', new_callable=mock_open, read_data="TOKEN=test_token\ntelegram_chat_id=test_chat_id")
    @patch('os.path.exists', return_value=True)
    def test_init_with_env_loading(self, mock_exists, mock_file):
        """Test that reporter works with environment loaded from file"""
        from src.helpers import load_env
        load_env("config/.env")

        reporter = TelegramReporter()
        self.assertEqual(reporter.url, "https://api.telegram.org/bottest_token/sendMessage")
        self.assertEqual(reporter.chat_id, "test_chat_id")

    @patch('os.path.exists', return_value=False)
    def test_env_file_not_found(self, mock_exists):
        """Test that FileNotFoundError is raised when .env file is missing"""
        from src.helpers import load_env
        with self.assertRaises(FileNotFoundError):
            load_env("missing_file.env")

    @patch('builtins.open', new_callable=mock_open, read_data="TOKEN='test_token'\ntelegram_chat_id='test_chat_id'")
    @patch('os.path.exists', return_value=True)
    def test_env_file_with_quoted_values(self, mock_exists, mock_file):
        """Test that quoted values in .env are properly handled"""
        from src.helpers import load_env
        load_env("config/.env")

        reporter = TelegramReporter()
        self.assertEqual(reporter.url, "https://api.telegram.org/bottest_token/sendMessage")
        self.assertEqual(reporter.chat_id, "test_chat_id")


if __name__ == '__main__':
    unittest.main()
