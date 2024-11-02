import unittest
import asyncio
import os
from datetime import datetime, timedelta
from utils.database import TaskDatabase

class TestTaskDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_scheduled_tasks.db"
        self.db = TaskDatabase(self.test_db_path)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.db.initialize())
        
    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
    def test_add_task(self):
        """Test adding a new task"""
        task_data = {
            'file': 'test.xlsx',
            'frequency': 'daily',
            'next_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'day_of_week': None,
            'day_of_month': None
        }
        
        task_id = self.loop.run_until_complete(self.db.add_task(task_data))
        self.assertIsNotNone(task_id)
        
        # Verify task was added
        task = self.loop.run_until_complete(self.db.get_task(task_id))
        self.assertEqual(task['file_name'], task_data['file'])
        self.assertEqual(task['frequency'], task_data['frequency'])
        
    def test_update_task_status(self):
        """Test updating task status"""
        # Add a task first
        task_data = {
            'file': 'test.xlsx',
            'frequency': 'daily',
            'next_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'day_of_week': None,
            'day_of_month': None
        }
        task_id = self.loop.run_until_complete(self.db.add_task(task_data))
        
        # Update status
        new_next_run = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        self.loop.run_until_complete(self.db.update_task_status(task_id, new_next_run, 'completed'))
        
        # Verify update
        task = self.loop.run_until_complete(self.db.get_task(task_id))
        self.assertEqual(task['status'], 'completed')
        
    def test_task_history(self):
        """Test task history tracking"""
        # Add a task
        task_data = {
            'file': 'test.xlsx',
            'frequency': 'daily',
            'next_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'day_of_week': None,
            'day_of_month': None
        }
        task_id = self.loop.run_until_complete(self.db.add_task(task_data))
        
        # Add history entries
        result = {'success': True, 'message': 'Task completed successfully'}
        self.loop.run_until_complete(self.db.add_task_history(task_id, 'success', result))
        
        # Get history
        history = self.loop.run_until_complete(self.db.get_task_history(task_id))
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['status'], 'success')
        
    def test_delete_task(self):
        """Test deleting a task"""
        # Add a task
        task_data = {
            'file': 'test.xlsx',
            'frequency': 'daily',
            'next_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'day_of_week': None,
            'day_of_month': None
        }
        task_id = self.loop.run_until_complete(self.db.add_task(task_data))
        
        # Add some history
        self.loop.run_until_complete(self.db.add_task_history(task_id, 'success'))
        
        # Delete task
        self.loop.run_until_complete(self.db.delete_task(task_id))
        
        # Verify task and history are deleted
        task = self.loop.run_until_complete(self.db.get_task(task_id))
        self.assertIsNone(task)
        
        history = self.loop.run_until_complete(self.db.get_task_history(task_id))
        self.assertEqual(len(history), 0)

if __name__ == '__main__':
    unittest.main()
