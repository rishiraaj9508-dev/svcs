class SVCSError(Exception):
    """Base class for all SVCS exceptions."""
    pass

class NotInitializedError(SVCSError):
    """Raised when an operation is attempted on an uninitialized directory."""
    pass

class AlreadyInitializedError(SVCSError):
    """Raised when attempting to initialize an already initialized directory."""
    pass

class FileNotFoundInProjectError(SVCSError):
    """Raised when trying to add a file that does not exist in the project."""
    pass

class EmptyIndexError(SVCSError):
    """Raised when trying to commit with no files staged."""
    pass

class EmptyCommitMessageError(SVCSError):
    """Raised when trying to commit without a message."""
    pass

class InvalidVersionError(SVCSError):
    """Raised when referring to a version that does not exist."""
    pass
