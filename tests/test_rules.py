from src.domain.rules.test_requirement import evaluate_test_requirement


def test_behavioral_diff_requires_tests():
    diff = "+ if (x > 0) { return 1; }"
    result = evaluate_test_requirement(diff)
    assert result.test_required is True
    assert result.priority == "high"


def test_non_behavioral_diff_can_skip_tests():
    diff = "+ // update comment\n+ logger.info('x')"
    result = evaluate_test_requirement(diff)
    assert result.test_required is False
