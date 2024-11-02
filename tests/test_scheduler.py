import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, time
from utils.scheduler import TaskScheduler

class TestTaskScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = TaskScheduler()
        
    def tearDown(self):
        self.scheduler.scheduler.shutdown()
        
    @patch('utils.scheduler.BackgroundScheduler')
    def test_scheduler_initialization(self, mock_scheduler):
        scheduler = TaskScheduler()
        self.assertTrue(mock_scheduler.called)
        self.assertTrue(mock_scheduler().start.called)
        
    @patch('datetime.datetime')
    def test_daily_schedule(self, mock_datetime):
        # Mock current time to be 10:00
        current_time = datetime(2024, 1, 1, 10, 0)
        mock_datetime.now.return_value = current_time
        
        # Schedule for 11:00
        schedule_time = time(11, 0)
        test_file = MagicMock()
        
        with patch.object(self.scheduler.scheduler, 'add_job') as mock_add_job:
            schedule_info = self.scheduler.schedule_task(schedule_time, test_file)
            self.assertTrue(mock_add_job.called)
            self.assertEqual(schedule_info['frequency'], 'daily')
            
    @patch('datetime.datetime')
    def test_weekly_schedule(self, mock_datetime):
        current_time = datetime(2024, 1, 1, 10, 0)
        mock_datetime.now.return_value = current_time
        
        schedule_time = time(11, 0)
        test_file = MagicMock()
        
        with patch.object(self.scheduler.scheduler, 'add_job') as mock_add_job:
            schedule_info = self.scheduler.schedule_task(
                schedule_time,
                test_file,
                frequency='weekly',
                day_of_week=1  # Tuesday
            )
            self.assertTrue(mock_add_job.called)
            self.assertEqual(schedule_info['frequency'], 'weekly')
            self.assertEqual(schedule_info['day_of_week'], 1)
            
    @patch('datetime.datetime')
    def test_monthly_schedule(self, mock_datetime):
        current_time = datetime(2024, 1, 1, 10, 0)
        mock_datetime.now.return_value = current_time
        
        schedule_time = time(11, 0)
        test_file = MagicMock()
        
        with patch.object(self.scheduler.scheduler, 'add_job') as mock_add_job:
            schedule_info = self.scheduler.schedule_task(
                schedule_time,
                test_file,
                frequency='monthly',
                day_of_month=15
            )
            self.assertTrue(mock_add_job.called)
            self.assertEqual(schedule_info['frequency'], 'monthly')
            self.assertEqual(schedule_info['day_of_month'], 15)

    def test_get_scheduled_tasks(self):
        test_file = MagicMock()
        test_file.name = "test.xlsx"
        
        # Add different types of schedules
        self.scheduler.schedule_task(time(10, 0), test_file)  # daily
        self.scheduler.schedule_task(time(11, 0), test_file, frequency='weekly', day_of_week=1)
        self.scheduler.schedule_task(time(12, 0), test_file, frequency='monthly', day_of_month=15)
        
        tasks = self.scheduler.get_scheduled_tasks()
        self.assertEqual(len(tasks), 3)
        
        frequencies = set(task['frequency'] for task in tasks)
        self.assertEqual(frequencies, {'daily', 'weekly', 'monthly'})

if __name__ == '__main__':
    unittest.main()
