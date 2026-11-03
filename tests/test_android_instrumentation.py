import pytest

from scripts.android_instrumentation import instrumentation_passed


@pytest.mark.parametrize('count', [1, 3])
def test_requires_every_requested_instrumentation_test_to_pass(count):
    report = f'OK ({count} {"test" if count == 1 else "tests"})\nINSTRUMENTATION_CODE: -1'
    assert instrumentation_passed(report, count)
    assert not instrumentation_passed(report, count + 1)


@pytest.mark.parametrize('marker', ['FAILURES!!!', 'INSTRUMENTATION_FAILED', 'INSTRUMENTATION_ABORTED'])
def test_instrumentation_failure_overrides_a_success_summary(marker):
    assert not instrumentation_passed(f'OK (3 tests)\n{marker}', 3)
