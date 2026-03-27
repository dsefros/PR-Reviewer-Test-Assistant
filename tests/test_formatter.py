from src.domain.formatters.output_formatter import format_output


def test_format_output_json():
    result = format_output({"a": 1}, as_json=True)
    assert '"a": 1' in result


def test_format_output_markdown():
    result = format_output({"items": ["x"]}, as_json=False)
    assert "## Items" in result
    assert "- x" in result
