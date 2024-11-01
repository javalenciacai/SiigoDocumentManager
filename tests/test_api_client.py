import unittest
from unittest.mock import patch, MagicMock
from utils.api_client import SiigoAPI

class TestSiigoAPI(unittest.TestCase):
    def setUp(self):
        self.api = SiigoAPI("test_user", "test_key")
        
    @patch('requests.post')
    def test_successful_authentication(self, mock_post):
        # Mock successful authentication response
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.api.authenticate()
        self.assertTrue(result)
        self.assertEqual(self.api.token, "test_token")
        
    @patch('requests.post')
    def test_failed_authentication(self, mock_post):
        # Mock failed authentication
        mock_post.side_effect = Exception("Authentication failed")
        
        result = self.api.authenticate()
        self.assertFalse(result)
        self.assertIsNone(self.api.token)
        
    @patch('requests.post')
    def test_create_journal_entry_success(self, mock_post):
        # Set up API token
        self.api.token = "test_token"
        
        # Mock successful journal entry creation
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "123", "status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        entry_data = {
            "date": "2024-01-01",
            "entries": [
                {
                    "account": "1010",
                    "description": "Test entry",
                    "debit": 1000.00,
                    "credit": 0.00
                }
            ]
        }
        
        result = self.api.create_journal_entry(entry_data)
        self.assertEqual(result["id"], "123")
        self.assertEqual(result["status"], "success")
        
    def test_create_journal_entry_no_auth(self):
        # Test creating entry without authentication
        with self.assertRaises(Exception) as context:
            self.api.create_journal_entry({})
        self.assertTrue("Not authenticated" in str(context.exception))
        
    @patch('requests.post')
    def test_create_journal_entry_api_error(self, mock_post):
        # Set up API token
        self.api.token = "test_token"
        
        # Mock API error
        mock_post.side_effect = Exception("API error")
        
        with self.assertRaises(Exception) as context:
            self.api.create_journal_entry({})
        self.assertTrue("API error" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
