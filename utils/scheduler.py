from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
    
    def schedule_task(self, time, file):
        """Schedule a task for daily execution at specified time"""
        # Convert time to datetime
        now = datetime.now()
        schedule_time = datetime.combine(now.date(), time)
        
        # If the time has passed for today, schedule for tomorrow
        if schedule_time <= now:
            schedule_time += timedelta(days=1)
        
        self.scheduler.add_job(
            self._process_scheduled_file,
            'interval',
            days=1,
            start_date=schedule_time,
            args=[file]
        )
    
    def _process_scheduled_file(self, file):
        """Process the scheduled file"""
        try:
            from main import process_entries
            from utils.excel_processor import ExcelProcessor
            
            processor = ExcelProcessor(file)
            df = processor.read_excel()
            results = process_entries(df)
            
            # Log results
            print(f"Scheduled processing completed at {datetime.now()}")
            print(f"Results: {results}")
            
        except Exception as e:
            print(f"Error in scheduled processing: {str(e)}")
