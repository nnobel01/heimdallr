"""
Logging utilities for Heimdallr
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "heimdallr", level: int = logging.INFO) -> logging.Logger:
    """Set up logger with console output"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatters
    console_format = "%(levelname)s - %(message)s"
    console_handler.setFormatter(logging.Formatter(console_format))
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "heimdallr") -> logging.Logger:
    """Get existing logger instance"""
    return logging.getLogger(name)
