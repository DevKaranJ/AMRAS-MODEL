class AmrasException(Exception):
    """
    Base exception for all custom exceptions in AMRAS.
    """
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class ConfigurationError(AmrasException):
    """
    Exception raised for configuration-related errors.
    """
    def __init__(self, message: str):
        super().__init__(message, code="CONFIGURATION_ERROR")

class ValidationError(AmrasException):
    """
    Exception raised for validation-related errors.
    """
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")

class ResourceNotFoundError(AmrasException):
    """
    Exception raised when a requested resource is not found.
    """
    def __init__(self, message: str):
        super().__init__(message, code="RESOURCE_NOT_FOUND")
