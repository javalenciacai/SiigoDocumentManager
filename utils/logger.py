import logging
import os
from datetime import datetime
import json
from pathlib import Path

class ErrorLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # Set up file handler for detailed logging
        self.log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
        self.logger = logging.getLogger('siigo_journal_processor')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for detailed logging
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Stream handler for console output
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_formatter = logging.Formatter('%(levelname)s: %(message)s')
        stream_handler.setFormatter(stream_formatter)
        self.logger.addHandler(stream_handler)
        
        # Initialize error statistics
        self.error_stats = {
            'api_errors': 0,
            'validation_errors': 0,
            'processing_errors': 0,
            'authentication_errors': 0
        }
        
    def log_error(self, error_type, message, details=None):
        """Log an error with details"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': str(message),
            'details': details
        }
        
        self.logger.error(f"{error_type}: {message}")
        if details:
            self.logger.debug(f"Error details: {json.dumps(details, indent=2)}")
            
        # Update error statistics
        if error_type in self.error_stats:
            self.error_stats[error_type] += 1
            
    def log_info(self, message):
        """Log information message"""
        self.logger.info(message)
        
    def get_error_stats(self):
        """Get current error statistics"""
        return self.error_stats
        
    def get_recent_errors(self, limit=10):
        """Get recent errors from log file"""
        recent_errors = []
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                error_lines = [line for line in lines if 'ERROR' in line]
                return error_lines[-limit:]
        except Exception as e:
            self.logger.error(f"Error reading log file: {str(e)}")
            return []

# Initialize global logger instance
error_logger = ErrorLogger()
