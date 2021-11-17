class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class WrongChannelError(Error):
    """Exception raised for messages in the wrong channel."""
    pass

class CommandNotFoundError(Error):
    pass
