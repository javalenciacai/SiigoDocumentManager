from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from utils.logger import error_logger
from utils.database import task_db
import asyncio
from apscheduler.jobstores.base import JobLookupError

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        error_logger.log_info("Task scheduler initialized")
    
    async def _save_task_to_db(self, task_data):
        """Save task to database"""
        return await task_db.add_task(task_data)
        
    async def _update_task_status(self, task_id, next_run, status):
        """Update task status in database"""
        await task_db.update_task_status(task_id, next_run, status)
        
    async def _add_task_history(self, task_id, status, result=None):
        """Add task execution history"""
        await task_db.add_task_history(task_id, status, result)
    
    def schedule_task(self, time, file, frequency='daily', day_of_week=None, day_of_month=None):
        """Schedule a task for recurring execution"""
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
            
            task_data = {
                'file': getattr(file, 'name', str(file)),
                'frequency': frequency,
                'next_run': schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
                'day_of_week': day_of_week,
                'day_of_month': day_of_month
            }
            
            # Save to database
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            task_id = loop.run_until_complete(self._save_task_to_db(task_data))
            
            # Extract trigger type and create job
            trigger = trigger_args.pop('trigger')
            job = self.scheduler.add_job(
                self._process_scheduled_file,
                trigger=trigger,
                **trigger_args,
                args=[file, task_id]
            )
            # Set job_id after creation
            job.id = str(task_id)
            
            error_logger.log_info(
                f"Task scheduled successfully for {schedule_time} with frequency {frequency}"
            )
            
            return task_data
            
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error scheduling task: {str(e)}",
                {'schedule_time': str(time), 'frequency': frequency}
            )
            raise Exception(f"Error scheduling task: {str(e)}")
    
    async def _process_scheduled_file(self, file, task_id):
        """Process the scheduled file"""
        try:
            from main import process_entries
            from utils.excel_processor import ExcelProcessor
            
            error_logger.log_info(f"Starting scheduled processing of file")
            
            processor = ExcelProcessor(file)
            df = processor.read_excel()
            results = process_entries(df)
            
            # Calculate success/failure stats
            success_count = sum(1 for r in results if r['status'] == 'Success')
            error_count = len(results) - success_count
            
            # Update task history
            result_summary = {
                'total': len(results),
                'success': success_count,
                'failed': error_count
            }
            
            await self._add_task_history(
                task_id,
                'success' if error_count == 0 else 'partial' if success_count > 0 else 'failed',
                result_summary
            )
            
            # Update next run time
            next_run = self.scheduler.get_job(str(task_id)).next_run_time
            await self._update_task_status(
                task_id,
                next_run.strftime('%Y-%m-%d %H:%M:%S'),
                'active'
            )
            
            error_logger.log_info(
                f"Scheduled processing completed: {success_count} successful, {error_count} failed"
            )
            
        except Exception as e:
            await self._add_task_history(task_id, 'failed', {'error': str(e)})
            error_logger.log_error(
                'processing_errors',
                f"Error in scheduled processing: {str(e)}",
                {'filename': getattr(file, 'name', 'unknown')}
            )
    
    async def get_scheduled_tasks(self):
        """Get list of all scheduled tasks with their details"""
        try:
            return await task_db.get_all_tasks(status='active')
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error fetching scheduled tasks: {str(e)}"
            )
            return []
            
    async def get_task_history(self, task_id, start_date=None, end_date=None):
        """Get task execution history"""
        try:
            return await task_db.get_task_history(task_id, start_date, end_date)
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error fetching task history: {str(e)}"
            )
            return []
            
    async def cancel_task(self, task_id):
        """Cancel a scheduled task"""
        try:
            # Get task from database first
            task = await task_db.get_task(task_id)
            if not task:
                raise Exception(f"Task {task_id} not found in database")
                
            # Remove from scheduler
            try:
                self.scheduler.remove_job(str(task_id))
            except JobLookupError:
                error_logger.log_info(f"Job {task_id} not found in scheduler, continuing with database cleanup")
                
            # Update database
            await task_db.delete_task(task_id)
            error_logger.log_info(f"Task {task_id} cancelled successfully")
            
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error cancelling task: {str(e)}"
            )
            raise Exception(f"Error cancelling task: {str(e)}")

def init_scheduler():
    """Initialize database with error handling"""
    try:
        # Initialize database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(task_db.initialize())
        error_logger.log_info("Database initialized successfully")
    except Exception as e:
        error_logger.log_error(
            'processing_errors',
            f"Error initializing database: {str(e)}"
        )
        raise

# Initialize scheduler and database
init_scheduler()
