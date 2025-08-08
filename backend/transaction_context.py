"""
Transaction Context Management System

This module provides a clean, thread-safe way to manage transaction GUIDs
throughout the application lifecycle without polluting method signatures.

The transaction GUID flows automatically through:
- MCP tool calls
- HTTP API requests  
- Service layer operations
- Database operations
- Logging entries

Key Features:
- Thread-safe using Python's contextvars
- Automatic GUID generation when needed
- Clean property-based access pattern
- Zero impact on existing method signatures
- Context manager for explicit GUID control

Usage Examples:
    # Automatic GUID generation
    guid = get_or_create_transaction_guid()
    
    # Explicit GUID setting
    with transaction_context("my-custom-guid"):
        # All operations within this block use the custom GUID
        pass
    
    # Property access in classes
    class MyService:
        @property
        def transaction_guid(self):
            return get_current_transaction_guid()
"""

from contextvars import ContextVar
from typing import Optional
import uuid
from contextlib import contextmanager

# Thread-safe context variable for storing transaction GUID
_transaction_guid_var: ContextVar[Optional[str]] = ContextVar('transaction_guid', default=None)


def generate_transaction_guid() -> str:
    """Generate a new UUID4 transaction GUID.
    
    Returns:
        str: A new UUID4 string in standard format (e.g., '550e8400-e29b-41d4-a716-446655440000')
        
    Examples:
        >>> guid = generate_transaction_guid()
        >>> len(guid)
        36
        >>> '-' in guid
        True
    """
    return str(uuid.uuid4())


def get_current_transaction_guid() -> Optional[str]:
    """Get the current transaction GUID from context.
    
    Returns the transaction GUID if one is set in the current context,
    or None if no GUID is active.
    
    Returns:
        Optional[str]: The current transaction GUID, or None if not set
        
    Examples:
        >>> # No GUID set initially
        >>> get_current_transaction_guid() is None
        True
        
        >>> # After setting GUID
        >>> token = set_transaction_guid("test-guid")
        >>> get_current_transaction_guid()
        'test-guid'
    """
    return _transaction_guid_var.get()


def get_or_create_transaction_guid() -> str:
    """Get the current transaction GUID, or create one if none exists.
    
    This is the main function for accessing transaction GUIDs. It will:
    1. Return the existing GUID if one is set in context
    2. Generate and set a new GUID if none exists
    3. Always return a valid GUID string
    
    This function is safe to call multiple times - it will not create
    duplicate GUIDs within the same context.
    
    Returns:
        str: The current or newly created transaction GUID
        
    Examples:
        >>> # First call creates GUID
        >>> guid1 = get_or_create_transaction_guid()
        >>> len(guid1)
        36
        
        >>> # Second call returns same GUID
        >>> guid2 = get_or_create_transaction_guid()
        >>> guid1 == guid2
        True
    """
    current_guid = _transaction_guid_var.get()
    if current_guid is None:
        current_guid = generate_transaction_guid()
        _transaction_guid_var.set(current_guid)
    return current_guid


def set_transaction_guid(guid: str) -> object:
    """Set a specific transaction GUID in the current context.
    
    This function allows you to explicitly set a transaction GUID,
    which is useful for:
    - MCP tool entry points
    - HTTP request handlers
    - Testing with known GUIDs
    
    Args:
        guid: The transaction GUID to set
        
    Returns:
        object: A context token that can be used with reset_transaction_guid()
                to restore the previous GUID when done
                
    Examples:
        >>> token = set_transaction_guid("my-test-guid")
        >>> get_current_transaction_guid()
        'my-test-guid'
        >>> reset_transaction_guid(token)
        >>> get_current_transaction_guid() is None
        True
    """
    return _transaction_guid_var.set(guid)


def reset_transaction_guid(token: object) -> None:
    """Reset the transaction GUID to its previous value.
    
    Use this with the token returned by set_transaction_guid()
    to restore the previous GUID state.
    
    Args:
        token: The token returned by set_transaction_guid()
        
    Examples:
        >>> # Save current state
        >>> token = set_transaction_guid("temp-guid")
        >>> # Do work...
        >>> # Restore previous state
        >>> reset_transaction_guid(token)
    """
    _transaction_guid_var.reset(token)


def clear_transaction_guid() -> None:
    """Clear the current transaction GUID from context.
    
    This sets the transaction GUID to None, which means
    get_current_transaction_guid() will return None and
    get_or_create_transaction_guid() will generate a new GUID.
    
    This is primarily useful for testing and cleanup scenarios.
    
    Examples:
        >>> set_transaction_guid("test-guid")
        >>> clear_transaction_guid()
        >>> get_current_transaction_guid() is None
        True
    """
    _transaction_guid_var.set(None)


@contextmanager
def transaction_context(guid: Optional[str] = None):
    """Context manager for transaction GUID lifecycle management.
    
    This context manager provides a clean way to set a transaction GUID
    for a specific block of code, with automatic cleanup when the block exits.
    
    Args:
        guid: Optional GUID to use. If None, a new GUID will be generated.
        
    Yields:
        str: The transaction GUID that was set for this context
        
    Examples:
        >>> # Use a specific GUID
        >>> with transaction_context("my-guid") as guid:
        ...     assert get_current_transaction_guid() == "my-guid"
        ...     assert guid == "my-guid"
        
        >>> # Auto-generate GUID
        >>> with transaction_context() as guid:
        ...     assert len(guid) == 36
        ...     assert get_current_transaction_guid() == guid
        
        >>> # GUID is cleared after context
        >>> get_current_transaction_guid() is None
        True
    """
    if guid is None:
        guid = generate_transaction_guid()
    
    token = set_transaction_guid(guid)
    try:
        yield guid
    finally:
        reset_transaction_guid(token)


# Convenience class for property-based access
class TransactionAware:
    """Mixin class providing transaction GUID property access.
    
    Classes can inherit from this mixin to get clean property-based
    access to the current transaction GUID without method signature changes.
    
    Examples:
        >>> class MyService(TransactionAware):
        ...     def do_work(self):
        ...         print(f"Working with GUID: {self.transaction_guid}")
        
        >>> with transaction_context("test-guid"):
        ...     service = MyService()
        ...     service.do_work()
        Working with GUID: test-guid
    """
    
    @property
    def transaction_guid(self) -> Optional[str]:
        """Get the current transaction GUID from context.
        
        Returns:
            Optional[str]: The current transaction GUID, or None if not set
        """
        return get_current_transaction_guid()
    
    @property
    def transaction_guid_or_create(self) -> str:
        """Get the current transaction GUID, creating one if needed.
        
        Returns:
            str: The current or newly created transaction GUID
        """
        return get_or_create_transaction_guid()


# Module-level convenience functions for backwards compatibility
def get_transaction_guid() -> Optional[str]:
    """Alias for get_current_transaction_guid() for backwards compatibility."""
    return get_current_transaction_guid()


def ensure_transaction_guid() -> str:
    """Alias for get_or_create_transaction_guid() for backwards compatibility."""
    return get_or_create_transaction_guid()