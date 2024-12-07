import unittest
from datetime import datetime
import pytz
from utils.timezone_handler import TimezoneHandler

class TestTimezoneHandler(unittest.TestCase):
    def setUp(self):
        self.timezone_handler = TimezoneHandler()
        self.user_timezone = "America/Bogota"
        self.test_datetime = datetime(2024, 12, 8, 9, 0, 0)  # 9:00 AM

    def test_convert_to_server_time(self):
        """Test conversion from user timezone to server timezone (UTC)"""
        # 9:00 AM Bogota time should be 14:00 UTC
        local_time = self.test_datetime
        utc_time = self.timezone_handler.convert_to_server_time(local_time, self.user_timezone)
        
        # Verify conversion
        self.assertEqual(utc_time.hour, 14)  # 9 AM Bogota = 14:00 UTC
        self.assertTrue(utc_time.tzinfo == pytz.UTC)

    def test_convert_to_user_time(self):
        """Test conversion from server timezone (UTC) to user timezone"""
        # Create a UTC time (14:00)
        utc_time = datetime(2024, 12, 8, 14, 0, 0, tzinfo=pytz.UTC)
        local_time = self.timezone_handler.convert_to_user_time(utc_time, self.user_timezone)
        
        # Verify conversion back to Bogota time (9:00 AM)
        self.assertEqual(local_time.hour, 9)
        self.assertEqual(str(local_time.tzinfo), "America/Bogota")

    def test_format_datetime(self):
        """Test datetime formatting with timezone information"""
        utc_time = datetime(2024, 12, 8, 14, 0, 0, tzinfo=pytz.UTC)
        formatted = self.timezone_handler.format_datetime(
            utc_time, 
            self.user_timezone,
            "%Y-%m-%d %H:%M:%S %Z"
        )
        
        # Verify format includes correct time and timezone
        self.assertIn("09:00:00", formatted)
        self.assertIn("-05", formatted)  # Bogota is UTC-5

    def test_naive_datetime_handling(self):
        """Test handling of naive datetime objects"""
        naive_datetime = datetime(2024, 12, 8, 9, 0, 0)  # No timezone info
        with self.assertRaises(ValueError):
            self.timezone_handler.convert_to_server_time(naive_datetime, None)

if __name__ == '__main__':
    unittest.main()
