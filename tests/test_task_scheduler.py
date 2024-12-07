import unittest
from datetime import datetime, time
import pytz
from utils.scheduler import TaskScheduler
from unittest.mock import Mock, patch

class TestTaskScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = TaskScheduler()
        self.company_name = "TEST_COMPANY"
        self.user_timezone = "America/Bogota"
        self.test_time = time(9, 0)  # 9:00 AM
        self.mock_file = Mock()
        self.mock_file.name = "test_file.xlsx"

    @patch('utils.scheduler.task_db')
    async def test_schedule_task_timezone_conversion(self, mock_db):
        """Test that task scheduling properly converts user timezone to UTC"""
        # Mock database operations
        mock_db.add_task.return_value = 1
        
        # Schedule a task for 9 AM Bogota time
        task_data = await self.scheduler.schedule_task(
            time=self.test_time,
            file=self.mock_file,
            company_name=self.company_name,
            user_timezone=self.user_timezone
        )
        
        # Verify the scheduled time is stored in UTC
        scheduled_time = datetime.strptime(task_data['next_run'], '%Y-%m-%d %H:%M:%S')
        self.assertEqual(scheduled_time.hour, 14)  # 9 AM Bogota = 14:00 UTC
        
        # Verify database was called with correct UTC time
        mock_db.add_task.assert_called_once()
        call_args = mock_db.add_task.call_args[0][0]
        self.assertIn('14:00:00', call_args['next_run'])

    @patch('utils.scheduler.task_db')
    async def test_schedule_task_next_day(self, mock_db):
        """Test that past times are scheduled for next day"""
        mock_db.add_task.return_value = 1
        
        # Use a time that has already passed today
        past_time = time(1, 0)  # 1:00 AM
        
        task_data = await self.scheduler.schedule_task(
            time=past_time,
            file=self.mock_file,
            company_name=self.company_name,
            user_timezone=self.user_timezone
        )
        
        # Verify the scheduled time is for tomorrow
        scheduled_time = datetime.strptime(task_data['next_run'], '%Y-%m-%d %H:%M:%S')
        tomorrow = datetime.now().date().day + 1
        self.assertEqual(scheduled_time.day, tomorrow)

if __name__ == '__main__':
    unittest.main()
