from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from utils.logger import error_logger

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        error_logger.log_info("Task scheduler initialized")
    
    def schedule_task(self, time, file, frequency='daily', day_of_week=None, day_of_month=None):
        """Schedule a task for recurring execution
        
        Args:
            time: Time to execute the task
            file: File to process
            frequency: Frequency of execution ('daily', 'weekly', 'monthly')
            day_of_week: Day of week for weekly scheduling (0-6, where 0=Monday)
            day_of_month: Day of month for monthly scheduling (1-31)
        """
        try:
            # Convert time to datetime
            now = datetime.now()
            schedule_time = datetime.combine(now.date(), time)
            
            # If the time has passed for today, schedule for next occurrence
            if schedule_time <= now:
                schedule_time += timedelta(days=1)
            
            trigger_args = {}
            
            if frequency == 'weekly' and day_of_week is not None:
                trigger_args = {
                    'trigger': 'cron',
                    'day_of_week': day_of_week,
                    'hour': time.hour,
                    'minute': time.minute
                }
            elif frequency == 'monthly' and day_of_month is not None:
                trigger_args = {
                    'trigger': 'cron',
                    'day': day_of_month,
                    'hour': time.hour,
                    'minute': time.minute
                }
            else:  # daily
                trigger_args = {
                    'trigger': 'interval',
                    'days': 1,
                    'start_date': schedule_time
                }
            
            self.scheduler.add_job(
                self._process_scheduled_file,
                **trigger_args,
                args=[file]
            )
            
            error_logger.log_info(
                f"Task scheduled successfully for {schedule_time} with frequency {frequency}"
            )
            
            return {
                'next_run': schedule_time,
                'frequency': frequency,
                'day_of_week': day_of_week,
                'day_of_month': day_of_month
            }
            
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error scheduling task: {str(e)}",
                {'schedule_time': str(time), 'frequency': frequency}
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

    def get_scheduled_tasks(self):
        """Get list of all scheduled tasks with their details"""
        jobs = self.scheduler.get_jobs()
        tasks = []
        for job in jobs:
            task = {
                'next_run': job.next_run_time.strftime("%Y-%m-%d %H:%M:%S"),
                'file': getattr(job.args[0], 'name', 'Unknown'),
                'frequency': 'daily'  # Default
            }
            
            # Determine frequency from trigger
            if hasattr(job.trigger, 'day_of_week'):
                task['frequency'] = 'weekly'
                task['day_of_week'] = job.trigger.fields[4]  # day_of_week field
            elif hasattr(job.trigger, 'day'):
                task['frequency'] = 'monthly'
                task['day_of_month'] = job.trigger.fields[2]  # day field
                
            tasks.append(task)
        return tasks
