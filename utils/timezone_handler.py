import pytz
from datetime import datetime

class TimezoneHandler:
    """Handles timezone conversions and user timezone detection"""
    
    def __init__(self):
        self.server_timezone = 'UTC'
    
    def get_user_timezone_script(self):
        """Returns JavaScript code for detecting user timezone"""
        return """
        <script>
            function sendTimezone() {
                const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                window.parent.postMessage({"timezone": timezone}, "*");
            }
            sendTimezone();
        </script>
        """
    
    def convert_to_server_time(self, dt: datetime, user_timezone: str) -> datetime:
        """Convert datetime from user timezone to server timezone"""
        if not isinstance(dt, datetime):
            raise ValueError("Input must be a datetime object")
        
        try:
            user_tz = pytz.timezone(user_timezone)
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {user_timezone}")
            
        server_tz = pytz.timezone(self.server_timezone)
        
        # Localize the datetime to user timezone first
        local_dt = user_tz.localize(dt)
        # Convert to server timezone
        return local_dt.astimezone(server_tz)
    
    def convert_to_user_time(self, dt: datetime, user_timezone: str) -> datetime:
        """Convert datetime from server timezone to user timezone"""
        if not isinstance(dt, datetime):
            raise ValueError("Input must be a datetime object")
        
        user_tz = pytz.timezone(user_timezone)
        server_tz = pytz.timezone(self.server_timezone)
        
        # Ensure datetime is aware of its timezone
        if dt.tzinfo is None:
            dt = server_tz.localize(dt)
        
        # Convert to user timezone
        return dt.astimezone(user_tz)
    
    def format_datetime(self, dt: datetime, user_timezone: str, format_str: str = '%Y-%m-%d %H:%M:%S %Z') -> str:
        """Format datetime in user timezone with specified format"""
        user_time = self.convert_to_user_time(dt, user_timezone)
        return user_time.strftime(format_str)
