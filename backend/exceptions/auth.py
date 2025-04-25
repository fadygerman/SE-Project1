class InvalidTokenException(Exception):
    """Exception raised when token validation fails"""
    def __init__(self, message="Invalid or expired token"):
        self.message = message
        super().__init__(self.message)

class MissingUserIdentifierException(Exception):
    """Exception raised when token doesn't contain required user identifier"""
    def __init__(self):
        self.message = "Invalid token: Missing user identifier"
        super().__init__(self.message)

class UserNotRegisteredException(Exception):
    """Exception raised when user is not registered in the system"""
    def __init__(self):
        self.message = "User not registered in the system"
        super().__init__(self.message)

class AuthenticationFailedException(Exception):
    """Generic exception for authentication failures"""
    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)

class IncompleteUserDataException(Exception):
    """Exception raised when user data is incomplete"""
    def __init__(self, missing_field):
        self.missing_field = missing_field
        self.message = f"User authenticated with Cognito but {missing_field} is missing or invalid. Please complete registration."
        super().__init__(self.message)

class UnauthorizedException(Exception):
    """Exception raised for unauthorized access"""
    def __init__(self, detail="Unauthorized"):
        self.detail = detail
        self.message = detail
        super().__init__(self.message)

class ForbiddenException(Exception):
    """Exception raised for forbidden access (authenticated but lacking permissions)"""
    def __init__(self, detail="Forbidden"):
        self.detail = detail
        self.message = detail
        super().__init__(self.message)

class ConfigurationError(Exception):
    """Exception raised for errors in application configuration."""
    def __init__(self, message="Configuration error"):
        self.message = message
        super().__init__(self.message)
