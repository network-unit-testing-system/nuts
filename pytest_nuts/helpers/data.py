from typing import Any, Optional


class NutsNornirResult:
    def __init__(
        self, result: Optional[Any] = None, failed: Optional[bool] = False, exception: Optional[BaseException] = None
    ):
        self.result = result
        self.failed = failed
        self.exception = exception

    def exception_or_failed(self):
        return self.exception or self.failed
