import pytest
from nuts.helpers.result import NutsResult
from nuts.context import NutsContext


class FakeContext(NutsContext):

    _RESULTS = {
        "failed": NutsResult(failed=True),
        "exception": NutsResult(exception=Exception("TestException")),
        "failed_exception": NutsResult(failed=True, exception=Exception("TestException")),
        "ok": NutsResult("TestData"),
    }
    
    def single_result(self, nuts_test_entry):
        return self._RESULTS[nuts_test_entry["kind"]]

CONTEXT = FakeContext

class TestCheckResult:
    @pytest.mark.nuts()
    def test_raises_error_if_exception(self, single_result):
        pass
