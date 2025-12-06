"""Custom exceptions for the Pup SDK."""


class PupError(Exception):
    """Base exception for all Pup SDK errors."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class PupConnectionError(PupError):
    """Raised when connection to Alberto fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONNECTION_ERROR")


class PupTimeoutError(PupError):
    """Raised when operation times out."""
    
    def __init__(self, message: str):
        super().__init__(message, "TIMEOUT_ERROR")


class PupAuthenticationError(PupError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "AUTH_ERROR")


class PupFileError(PupError):
    """Raised when file operations fail."""
    
    def __init__(self, message: str, file_path: str = None):
        super().__init__(message, "FILE_ERROR")
        self.file_path = file_path


class PupShellError(PupError):
    """Raised when shell commands fail."""
    
    def __init__(self, message: str, exit_code: int = None):
        super().__init__(message, "SHELL_ERROR")
        self.exit_code = exit_code


class PupValidationError(PupError):
    """Raised when validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")