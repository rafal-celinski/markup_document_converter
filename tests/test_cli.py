import pytest
from typer.testing import CliRunner
from markup_document_converter.cli import app


@pytest.fixture
def runner():
    return CliRunner()


class TestCLICommands:
    def test_version(self, runner):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "markup_document_converter version" in result.stdout

    def test_list_formats(self, runner):
        result = runner.invoke(app, ["list-formats"])
        assert result.exit_code == 0
        assert "Input parsers:" in result.stdout
        assert "Output converters:" in result.stdout
        assert "• markdown" in result.stdout
        assert "• typst" in result.stdout

    def test_convert_markdown_to_typst_basic(self, runner, tmp_path):
        input_file = tmp_path / "test.md"
        input_file.write_text("# Test\n\nHello World")

        result = runner.invoke(app, ["convert", str(input_file), "--to", "typst"])
        assert result.exit_code == 0
        assert "= Test" in result.stdout
        assert "Hello World" in result.stdout

    def test_convert_with_output_file(self, runner, tmp_path):
        input_file = tmp_path / "test.md"
        output_file = tmp_path / "output.typ"
        input_file.write_text("# Test\n\nHello World")

        result = runner.invoke(
            app,
            ["convert", str(input_file), "--to", "typst", "--output", str(output_file)],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "= Test" in content
        assert "Hello World" in content

    def test_convert_nonexistent_file(self, runner):
        result = runner.invoke(app, ["convert", "nonexistent.md", "--to", "typst"])
        assert result.exit_code != 0
        assert "does not exist" in result.stdout

    def test_convert_invalid_format(self, runner, tmp_path):
        input_file = tmp_path / "test.md"
        input_file.write_text("# Test")

        result = runner.invoke(app, ["convert", str(input_file), "--to", "invalid"])
        assert result.exit_code != 0
        assert "No converter registered for 'invalid'" in result.stdout

    def test_convert_complex_markdown(self, runner, tmp_path):
        input_file = tmp_path / "test.md"
        input_file.write_text("# Complex\n\nThis is a CLI smoke-test.")

        result = runner.invoke(app, ["convert", str(input_file), "--to", "typst"])
        assert result.exit_code == 0
        assert "= Complex" in result.stdout
        assert r"This is a CLI smoke\-test." in result.stdout
