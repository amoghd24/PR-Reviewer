"""Centralized logging configuration for the PR reviewer system."""

import logging
import os
from typing import Optional


def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
        
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use provided level or default to INFO
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Default format string
    default_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_format = format_string or default_format
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Avoid adding multiple handlers if logger already configured
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with default configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return setup_logger(name)