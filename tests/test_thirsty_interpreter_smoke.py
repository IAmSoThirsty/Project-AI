from thirsty_lang.interpreter_smoke import run_thirsty_interpreter_smoke


def test_thirsty_interpreter_smoke():
    result = run_thirsty_interpreter_smoke()

    assert result.passed
    assert result.output == result.expected_output
    assert result.variables == result.expected_variables
