import pytest
from nuts.helpers.result import NutsResult, AbstractResultExtractor
from nuts.context import NutsContext


class FakeExtractor(AbstractResultExtractor):
    _RESULTS = {
        "failed": NutsResult(failed=True),
        "exception": NutsResult(exception=Exception("TestException")),
        "failed_exception": NutsResult(
            failed=True, exception=Exception("TestException")
        ),
        "ok": NutsResult("TestData"),
    }

    def single_result(self, nuts_test_entry):
        return self._RESULTS[nuts_test_entry["kind"]]


class FakeContext(NutsContext):
    def nuts_extractor(self) -> AbstractResultExtractor:
        return FakeExtractor(self)


CONTEXT = FakeContext


class TestCheckResult:
    @pytest.mark.nuts()
    def test_raises_error_if_exception(self, single_result):
        pass
