from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from utils.logger import error_logger

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        error_logger.log_info("Task scheduler initialized")
    
    def schedule_task(self, time, file):
        """Schedule a task for daily execution at specified time"""
        try:
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
            
            error_logger.log_info(
                f"Task scheduled successfully for {schedule_time}"
            )
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error scheduling task: {str(e)}",
                {'schedule_time': str(time)}
            )
            raise Exception(f"Error scheduling task: {str(e)}")
    
    def _process_scheduled_file(self, file):
        """Process the scheduled file"""
        try:
            from main import process_entries
            from utils.excel_processor import ExcelProcessor
            
            error_logger.log_info(f"Starting scheduled processing of file")
            
            processor = ExcelProcessor(file)
            df = processor.read_excel()
            results = process_entries(df)
            
            # Log results
            success_count = sum(1 for r in results if r['status'] == 'Success')
            error_count = len(results) - success_count
            
            error_logger.log_info(
                f"Scheduled processing completed: {success_count} successful, {error_count} failed"
            )
            
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error in scheduled processing: {str(e)}",
                {'filename': getattr(file, 'name', 'unknown')}
            )
