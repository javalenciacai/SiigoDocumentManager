import aiosqlite
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import json

class TaskDatabase:
    def __init__(self, db_path: str = "scheduled_tasks.db"):
        self.db_path = db_path
        
    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create scheduled_tasks table with company_name field
            await db.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    next_run TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    day_of_week INTEGER,
                    day_of_month INTEGER
                )
            ''')
            
            # Create task_history table with company_name field
            await db.execute('''
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    task_id INTEGER NOT NULL,
                    run_time TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    FOREIGN KEY (task_id) REFERENCES scheduled_tasks (id)
                )
            ''')
            await db.commit()
    
    async def add_task(self, task_data: Dict) -> int:
        """Add a new scheduled task"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO scheduled_tasks 
                (company_name, file_name, frequency, next_run, status, day_of_week, day_of_month)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_data['company_name'],
                task_data['file'],
                task_data['frequency'],
                task_data['next_run'],
                'active',
                task_data.get('day_of_week'),
                task_data.get('day_of_month')
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def update_task_status(self, task_id: int, next_run: str, status: str, company_name: str):
        """Update task status and next run time"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE scheduled_tasks 
                SET next_run = ?, status = ?
                WHERE id = ? AND company_name = ?
            ''', (next_run, status, task_id, company_name))
            await db.commit()
    
    async def add_task_history(self, task_id: int, company_name: str, status: str, result: Optional[Dict] = None):
        """Add task execution history"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO task_history (company_name, task_id, run_time, status, result)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
            ''', (company_name, task_id, status, json.dumps(result) if result else None))
            await db.commit()
    
    async def get_task(self, task_id: int, company_name: str) -> Dict:
        """Get task details by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM scheduled_tasks 
                WHERE id = ? AND company_name = ?
            ''', (task_id, company_name))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_all_tasks(self, company_name: str, status: Optional[str] = None) -> List[Dict]:
        """Get all scheduled tasks for a company"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM scheduled_tasks WHERE company_name = ?'
            params = [company_name]
            if status:
                query += ' AND status = ?'
                params.append(status)
            cursor = await db.execute(query + ' ORDER BY next_run', params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_task_history(self, task_id: int, company_name: str,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> List[Dict]:
        """Get task execution history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM task_history WHERE task_id = ? AND company_name = ?'
            params = [task_id, company_name]
            
            if start_date:
                query += ' AND run_time >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND run_time <= ?'
                params.append(end_date)
                
            cursor = await db.execute(query + ' ORDER BY run_time DESC', params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def delete_task(self, task_id: int, company_name: str):
        """Delete a scheduled task"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM task_history WHERE task_id = ? AND company_name = ?', 
                           (task_id, company_name))
            await db.execute('DELETE FROM scheduled_tasks WHERE id = ? AND company_name = ?', 
                           (task_id, company_name))
            await db.commit()

# Create global database instance
task_db = TaskDatabase()

def init_database():
    """Initialize database tables"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task_db.initialize())
