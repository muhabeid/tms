"""
Centralized error handling utility for the TMS system.
Provides consistent error logging and handling across all modules.
"""

import traceback
import datetime
import os
from typing import Optional
from pathlib import Path


class ErrorHandler:
    """Centralized error handler for logging and error management."""
    
    def __init__(self, log_dir: str = "logs", module_name: str = "general"):
        """
        Initialize the error handler.
        
        Args:
            log_dir: Directory to store log files
            module_name: Name of the module for log file naming
        """
        self.log_dir = Path(log_dir)
        self.module_name = module_name
        self.log_file = self.log_dir / f"{module_name}_error.log"
        
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
    
    def log_error(self, error: Exception, context: str = "", additional_info: Optional[dict] = None) -> str:
        """
        Log an error with full context and traceback.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            additional_info: Optional dictionary with additional information
            
        Returns:
            The formatted error message that was logged
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build error message
        error_msg = f"\n{'='*80}\n"
        error_msg += f"[{timestamp}] ERROR in {self.module_name}\n"
        error_msg += f"Context: {context}\n"
        error_msg += f"Error Type: {type(error).__name__}\n"
        error_msg += f"Error Message: {str(error)}\n"
        
        if additional_info:
            error_msg += f"Additional Info: {additional_info}\n"
        
        error_msg += f"\nTraceback:\n{traceback.format_exc()}\n"
        error_msg += f"{'='*80}\n"
        
        # Print to console
        print(error_msg)
        
        # Write to log file (append mode)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(error_msg)
        except Exception as log_error:
            print(f"Failed to write to log file: {log_error}")
        
        return error_msg
    
    def log_api_error(self, error: Exception, endpoint: str = "", method: str = "", 
                     request_data: Optional[dict] = None, user_id: Optional[str] = None) -> str:
        """
        Specialized logging for API endpoint errors.
        
        Args:
            error: The exception that occurred
            endpoint: API endpoint where error occurred
            method: HTTP method (GET, POST, etc.)
            request_data: Optional request data
            user_id: Optional user ID for tracking
            
        Returns:
            The formatted error message that was logged
        """
        context = f"API Endpoint: {method} {endpoint}"
        additional_info = {}
        
        if request_data:
            additional_info["request_data"] = request_data
        if user_id:
            additional_info["user_id"] = user_id
            
        return self.log_error(error, context, additional_info)
    
    def get_log_summary(self, lines: int = 10) -> str:
        """
        Get a summary of recent log entries.
        
        Args:
            lines: Number of lines to include in summary
            
        Returns:
            String containing recent log entries
        """
        try:
            if not self.log_file.exists():
                return "No error logs found."
            
            with open(self.log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return "".join(recent_lines)
        except Exception as e:
            return f"Error reading log file: {e}"


# Global error handler instances for each module
transport_error_handler = ErrorHandler(module_name="transport")
finance_error_handler = ErrorHandler(module_name="finance")
hr_error_handler = ErrorHandler(module_name="hr")
express_error_handler = ErrorHandler(module_name="express")
fuel_error_handler = ErrorHandler(module_name="fuel")
workshop_error_handler = ErrorHandler(module_name="workshop")


def get_error_handler(module_name: str) -> ErrorHandler:
    """
    Get the appropriate error handler for a module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        ErrorHandler instance for the module
    """
    handlers = {
        "transport": transport_error_handler,
        "finance": finance_error_handler,
        "hr": hr_error_handler,
        "express": express_error_handler,
        "fuel": fuel_error_handler,
        "workshop": workshop_error_handler,
    }
    
    return handlers.get(module_name, ErrorHandler(module_name=module_name))