import structlog
import logging
import logging.handlers
from pathlib import Path
from typing import Any, Dict, Optional
import os
import re
import sys
from datetime import datetime


class PlainTextFormatter(logging.Formatter):
    """Custom formatter for plain text file logging without ANSI escape sequences.
    
    Formats structured log entries into readable plain text suitable for
    viewing in standard text editors.
    """
    
    def format(self, record):
        """Format a log record as plain text.
        
        Converts structured log data into a readable format:
        [timestamp] [LEVEL] [logger] message key=value key=value
        
        Args:
            record: The LogRecord to format.
            
        Returns:
            A formatted plain text string.
        """
        try:
            # Parse the structured log data
            if hasattr(record, 'msg') and isinstance(record.msg, dict):
                data = record.msg
            else:
                # Try to parse as a structured message
                msg = str(record.getMessage())
                if msg.startswith('{') and msg.endswith('}'):
                    import json
                    try:
                        data = json.loads(msg)
                    except:
                        data = {'event': msg}
                else:
                    data = {'event': msg}
            
            # Extract main components
            timestamp = data.get('timestamp', datetime.utcnow().isoformat() + 'Z')
            level = data.get('level', record.levelname).upper()
            logger_name = data.get('logger', record.name)
            event = data.get('event', '')
            
            # Build the base message
            parts = [
                f"[{timestamp}]",
                f"[{level}]",
                f"[{logger_name}]" if logger_name else "",
                event
            ]
            
            base_message = " ".join(filter(None, parts))
            
            # Add additional key-value pairs
            extras = []
            skip_keys = {'timestamp', 'level', 'logger', 'event'}
            
            for key, value in data.items():
                if key not in skip_keys and value is not None:
                    extras.append(f"{key}={value}")
            
            if extras:
                return f"{base_message} | {' '.join(extras)}"
            else:
                return base_message
                
        except Exception:
            # Fallback to standard formatting
            return super().format(record)


class DualOutputProcessor:
    """Processor to handle dual output to console and file with different formats.
    
    This processor intercepts log messages and sends them to file handlers
    with plain text formatting while allowing console output to use colors.
    """
    
    def __init__(self, file_handler, debug_mode=False):
        """Initialize the dual output processor.
        
        Args:
            file_handler: The file handler to write plain text logs to.
            debug_mode: Whether debug mode is enabled.
        """
        self.file_handler = file_handler
        self.debug_mode = debug_mode
    
    def __call__(self, logger, method_name, event_dict):
        """Process a log event for dual output.
        
        Args:
            logger: The logger instance.
            method_name: The logging method name (info, error, etc.).
            event_dict: The structured log event data.
            
        Returns:
            The event_dict unchanged (for console processing).
        """
        # Create a log record for file output
        if self.file_handler:
            try:
                # Create a plain text version for file
                record = logging.LogRecord(
                    name=event_dict.get('logger', ''),
                    level=getattr(logging, method_name.upper(), logging.INFO),
                    pathname='',
                    lineno=0,
                    msg=event_dict,
                    args=(),
                    exc_info=None
                )
                
                # Write to file handler
                self.file_handler.emit(record)
                
            except Exception:
                # If file logging fails, don't break console logging
                pass
        
        return event_dict

def configure_logging(
    debug: bool = False, 
    log_file_path: Optional[str] = None,
    log_level: str = "INFO",
    rotation_hours: int = 1,
    retention_days: int = 7
) -> None:
    """Configure structured logging for the application.
    
    Sets up both console and file logging with structured log formatting
    using structlog. Console output uses colored formatting in debug mode,
    while file output always uses plain text format for readability.
    
    Args:
        debug: Whether to enable debug mode with colored console output.
            Defaults to False.
        log_file_path: Path to the log file. If None, only console logging
            is enabled. Defaults to None.
        log_level: The logging level as a string (DEBUG, INFO, WARNING, ERROR).
            Defaults to "INFO".
        rotation_hours: Hours between log file rotations. Defaults to 1.
        retention_days: Number of days to retain rotated log files.
            Defaults to 7.
            
    Examples:
        >>> configure_logging(debug=True)  # Debug mode with console only
        >>> configure_logging(log_file_path="logs/app.log")  # With file logging
        >>> configure_logging(log_level="DEBUG", retention_days=30)
    """
    
    # Set log level
    if debug:
        level = logging.DEBUG
    else:
        level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure handlers
    handlers = []
    
    # Console handler (always present) - uses structlog formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (if log file path is provided) - uses plain text formatting
    file_handler = None
    if log_file_path:
        # Ensure log directory exists
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler (rotates every hour)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file_path,
            when='H',  # Rotate hourly
            interval=rotation_hours,  # Rotation interval
            backupCount=retention_days * 24,  # Keep logs for specified days
            encoding='utf-8',
            utc=True  # Use UTC for rotation timing
        )
        file_handler.setLevel(level)
        
        # Set file naming pattern for rotated logs
        file_handler.suffix = "%Y-%m-%d_%H"
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}$")
        
        # Plain text formatter for file logs (readable in text editors)
        file_formatter = PlainTextFormatter()
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
        
        print(f"File logging enabled: {log_file_path} (rotation: {rotation_hours}h, retention: {retention_days}d)")
    
    # Configure standard logging to intercept non-structlog messages
    logging.basicConfig(
        level=level,
        handlers=[console_handler],  # Only console handler in basicConfig
        format="%(message)s"
    )
    
    # Configure third-party loggers to use consistent formatting
    third_party_loggers = [
        'uvicorn', 'uvicorn.access', 'uvicorn.error', 'fastapi',
        'sqlalchemy.engine', 'sqlalchemy', 'alembic'
    ]
    
    for logger_name in third_party_loggers:
        third_party_logger = logging.getLogger(logger_name)
        # In debug mode, let them propagate to get colored output
        if debug:
            third_party_logger.propagate = True
        else:
            third_party_logger.handlers = [console_handler]
            third_party_logger.propagate = False
    
    # Set SQLAlchemy engine logging to INFO level to reduce noise but keep colors
    if debug:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Configure structlog with dual output support
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
    ]
    
    # Add dual output processor if we have file logging (must be before renderer)
    if file_handler:
        processors.append(DualOutputProcessor(file_handler, debug))
    
    # Choose renderer based on output type (for console)
    if debug:
        # Use colored console renderer with pretty formatting
        # Force colors if stdout is a terminal or if we're in development
        use_colors = sys.stdout.isatty() or os.getenv('FORCE_COLOR') == '1' or debug
        processors.append(structlog.dev.ConsoleRenderer(
            colors=use_colors,
            force_colors=use_colors,
            repr_native_str=False,
            exception_formatter=structlog.dev.plain_traceback
        ))
    else:
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance.
    
    Creates or retrieves a structured logger instance bound to the
    specified name. The logger will use the configuration set by
    configure_logging().
    
    Args:
        name: The name for the logger, typically __name__ of the
            calling module.
            
    Returns:
        A structlog BoundLogger instance configured for structured logging.
        
    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started", version="1.0.0")
        >>> logger.error("Database error", error="Connection failed", retries=3)
    """
    return structlog.get_logger(name)

def log_api_request(method: str, path: str, **kwargs) -> Dict[str, Any]:
    """Create a log context for API requests.
    
    Helper function to create consistent log entries for incoming API
    requests. Adds standard fields for request tracking.
    
    Args:
        method: The HTTP method (GET, POST, etc.).
        path: The request path/endpoint.
        **kwargs: Additional context to include in the log entry.
        
    Returns:
        A dictionary containing the log context with standardized fields.
        
    Examples:
        >>> context = log_api_request("POST", "/api/stories", user_id=123)
        >>> logger.info("Request received", **context)
    """
    return {
        "event": "api_request",
        "method": method,
        "path": path,
        **kwargs
    }

def log_api_response(status_code: int, duration_ms: float, **kwargs) -> Dict[str, Any]:
    """Create a log context for API responses.
    
    Helper function to create consistent log entries for API responses.
    Includes performance metrics and response status.
    
    Args:
        status_code: The HTTP response status code.
        duration_ms: Request processing duration in milliseconds.
        **kwargs: Additional context to include in the log entry.
        
    Returns:
        A dictionary containing the log context with standardized fields.
        
    Examples:
        >>> context = log_api_response(200, 45.3, bytes_sent=1024)
        >>> logger.info("Request completed", **context)
    """
    return {
        "event": "api_response",
        "status_code": status_code,
        "duration_ms": duration_ms,
        **kwargs
    }

def log_service_call(service: str, method: str, **kwargs) -> Dict[str, Any]:
    """Create a log context for service calls.
    
    Helper function to create consistent log entries for internal service
    calls, such as calls to LLM services or database operations.
    
    Args:
        service: The name of the service being called.
        method: The method or operation being performed.
        **kwargs: Additional context to include in the log entry.
        
    Returns:
        A dictionary containing the log context with standardized fields.
        
    Examples:
        >>> context = log_service_call("openai", "generate_story", 
        ...                           model="gpt-3.5-turbo", tokens=500)
        >>> logger.info("Calling LLM service", **context)
    """
    return {
        "event": "service_call",
        "service": service,
        "method": method,
        **kwargs
    }