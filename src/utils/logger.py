"""
Logger utility module for the tech-news-curator application.

This module provides centralized logging configuration for consistent
log formatting across the entire application.
"""

import os
import logging
import logging.handlers
from typing import Optional

def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Configure application-wide logging with consistent formatting.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional file to save logs to (relative to log_dir)
        console: Whether to output logs to console
        log_dir: Directory to store log files
        
    Returns:
        Configured root logger instance
    """
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        file_path = os.path.join(log_dir, log_file)
        
        # Configure rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Quiet some noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return root_logger