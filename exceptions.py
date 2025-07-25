from typing import Optional
from logging_config import get_logger

logger = get_logger(__name__)

class Error(Exception):
    """Base exception for application errors.
    
    This is the base exception class for all custom exceptions in the
    application. It provides consistent error handling with error codes
    and logging capabilities.
    
    Args:
        message: A descriptive error message.
        error_code: An optional error code for categorizing the error.
            
    Attributes:
        message: The error message.
        error_code: The error code (if provided).
        
    Examples:
        >>> raise Error("Something went wrong", "GENERAL_ERROR")
        >>> try:
        ...     raise Error("Invalid input")
        ... except Error as e:
        ...     print(e.message)
        Invalid input
    """
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        logger.warning("Exception created", 
                      exception_type=self.__class__.__name__,
                      message=message,
                      error_code=error_code)
        super().__init__(self.message)

class ServiceError(Error):
    """Exception for service-related errors.
    
    This exception is raised for errors that occur within the service layer,
    including API communication errors, service initialization failures, and
    other service-specific issues.
    
    Inherits from:
        Error: Base exception for the application.
        
    Examples:
        >>> raise ServiceError("Service unavailable", "SERVICE_UNAVAILABLE")
    """
    pass

class APIKeyError(ServiceError):
    """Raised when API key is missing or invalid.
    
    This exception indicates issues with API authentication, such as
    missing API keys in configuration or invalid/expired API keys.
    
    Args:
        message: Custom error message. Defaults to "Invalid or missing API key".
        
    Inherits from:
        ServiceError: Base exception for service errors.
        
    Examples:
        >>> raise APIKeyError()
        >>> raise APIKeyError("OpenAI API key not found in environment")
    """
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, "API_KEY_ERROR")

class APIConnectionError(ServiceError):
    """Raised when unable to connect to external API.
    
    This exception is raised when network connectivity issues prevent
    communication with external APIs (OpenAI, OpenRouter, etc.).
    
    Args:
        message: Custom error message. Defaults to "Failed to connect to API".
        
    Inherits from:
        ServiceError: Base exception for service errors.
        
    Examples:
        >>> raise APIConnectionError()
        >>> raise APIConnectionError("Unable to reach OpenAI servers")
    """
    def __init__(self, message: str = "Failed to connect to API"):
        super().__init__(message, "API_CONNECTION_ERROR")

class APIRateLimitError(ServiceError):
    """Raised when API rate limit is exceeded.
    
    This exception indicates that the application has exceeded the rate
    limits imposed by the external API provider.
    
    Args:
        message: Custom error message. Defaults to "API rate limit exceeded".
        
    Inherits from:
        ServiceError: Base exception for service errors.
        
    Examples:
        >>> raise APIRateLimitError()
        >>> raise APIRateLimitError("OpenAI rate limit: 3 requests per minute exceeded")
    """
    def __init__(self, message: str = "API rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_ERROR")

class ValidationError(Error):
    """Raised when input validation fails.
    
    This exception is raised when user input fails validation checks,
    such as invalid character names, empty inputs, or inputs containing
    potentially malicious content.
    
    Args:
        message: Custom error message. Defaults to "Input validation failed".
        
    Inherits from:
        Error: Base exception for the application.
        
    Examples:
        >>> raise ValidationError("Character name cannot be empty")
        >>> raise ValidationError("Name contains invalid characters")
    """
    def __init__(self, message: str = "Input validation failed"):
        super().__init__(message, "VALIDATION_ERROR")


class TimeoutError(Error):
    """Raised when operation times out.
    
    This exception is raised when an operation exceeds its allocated
    time limit, such as API calls taking too long or operations
    exceeding the timeout threshold.
    
    Args:
        message: Custom error message. Defaults to "Operation timed out".
        
    Inherits from:
        Error: Base exception for the application.
        
    Examples:
        >>> raise TimeoutError()
        >>> raise TimeoutError("Operation exceeded 30 second timeout")
    """
    def __init__(self, message: str = "Operation timed out"):
        super().__init__(message, "TIMEOUT_ERROR")


# Backwards compatibility alias (deprecated)
StoryGeneratorError = Error