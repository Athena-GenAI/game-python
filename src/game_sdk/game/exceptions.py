"""
Custom exceptions for the GAME SDK.
"""

class GameSDKError(Exception):
    """Base exception for all GAME SDK errors."""
    pass

class ValidationError(GameSDKError):
    """Raised when input validation fails."""
    def __init__(self, message="Validation failed", errors=None):
        super().__init__(message)
        self.errors = errors or {}

class APIError(GameSDKError):
    """Raised when API requests fail."""
    def __init__(self, message="API request failed", status_code=None, response_json=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_json = response_json

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass

class StateError(GameSDKError):
    """Raised when there are issues with state management."""
    pass
