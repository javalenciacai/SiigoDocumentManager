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
    def test_schedule_task_future_time(self, mock_datetime):
        # Mock current time to be 10:00
        current_time = datetime(2024, 1, 1, 10, 0)
        mock_datetime.now.return_value = current_time
        
        # Schedule for 11:00
        schedule_time = time(11, 0)
        test_file = MagicMock()
        
        with patch.object(self.scheduler.scheduler, 'add_job') as mock_add_job:
            self.scheduler.schedule_task(schedule_time, test_file)
            self.assertTrue(mock_add_job.called)
            
    @patch('datetime.datetime')
    def test_schedule_task_past_time(self, mock_datetime):
        # Mock current time to be 15:00
        current_time = datetime(2024, 1, 1, 15, 0)
        mock_datetime.now.return_value = current_time
        
        # Schedule for 14:00 (should schedule for next day)
        schedule_time = time(14, 0)
        test_file = MagicMock()
        
        with patch.object(self.scheduler.scheduler, 'add_job') as mock_add_job:
            self.scheduler.schedule_task(schedule_time, test_file)
            self.assertTrue(mock_add_job.called)
            
    @patch('utils.scheduler.ExcelProcessor')
    def test_process_scheduled_file(self, mock_processor):
        test_file = MagicMock()
        mock_processor.return_value.read_excel.return_value = MagicMock()
        
        # Test successful processing
        self.scheduler._process_scheduled_file(test_file)
        self.assertTrue(mock_processor.called)
        
    @patch('utils.scheduler.ExcelProcessor')
    def test_process_scheduled_file_error(self, mock_processor):
        test_file = MagicMock()
        mock_processor.side_effect = Exception("Processing error")
        
        # Test error handling
        self.scheduler._process_scheduled_file(test_file)
        # Should not raise exception but log the error

if __name__ == '__main__':
    unittest.main()
