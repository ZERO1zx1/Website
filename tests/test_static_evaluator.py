from backend.services.static_evaluator import evaluate_static


def test_html_requirement_passes_without_sandbox():
    result = evaluate_static(
        '<form><label for="email">Email</label><input id="email" required></form>',
        'html',
        [{'expected_output': 'required'}],
    )
    assert result['mode'] == 'static'
    assert result['status'] == 'accepted'
    assert result['passed_tests'] == 1


def test_css_requirement_failure_is_rejected():
    result = evaluate_static(
        '.card { color: red; }',
        'css',
        [{'expected_output': 'display: flex'}, {'expected_output': 'box-sizing: border-box', 'is_hidden': True}],
    )
    assert result['status'] == 'wrong_answer'
    assert result['failed_tests'] == 2
    assert result['test_results'][1]['is_hidden'] is True
