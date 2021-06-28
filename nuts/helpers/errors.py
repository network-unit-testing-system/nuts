class Error(Exception):
    """Base class for exceptions."""


class NutsSetupError(Error):
    """Errors caused during the setup of Nuts."""

    def __init__(self, message: str):
        super(NutsSetupError, self).__init__(message)


class NutsUsageError(Error):
    """Errors caused by the user."""


class NutsNornirError(Error):
    """Errors caused by nornir."""


class NutsUnvalidatedResultError(Error):
    """Internal error: An unvalidated NutsResult was accessed."""
