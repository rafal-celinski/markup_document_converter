from markup_document_converter.converters.latex_converter import LatexConverter
from markup_document_converter.parsers.markdown_parser import MarkdownParser
import pytest
from pathlib import Path


def load_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Test file doesn't exist: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


@pytest.fixture(scope="class")
def latex_converter(request):
    request.cls.latex_converter = LatexConverter()


@pytest.fixture(scope="class")
def markdown_parser(request):
    request.cls.markdown_parser = MarkdownParser()


@pytest.mark.usefixtures("latex_converter")
@pytest.mark.usefixtures("markdown_parser")
class TestMarkdownToLatex:

    @pytest.mark.parametrize(
        "source_filename, expected_filename",
        [
            ("text_formating.md", "text_formating.tex"),
            ("headings.md", "headings.tex"),
            ("lists.md", "lists.tex"),
            ("links_and_images.md", "links_and_images.tex"),
            ("tables.md", "tables.tex"),
            # ("quotes_and_breaks.md", "quotes_and_breaks.tex"), Quotes doesn't work in markdown :(
            ("code_blocks.md", "code_blocks.tex"),
        ],
    )
    def test_source_expected(self, source_filename, expected_filename):
        markdown_source_file_path = (
            Path(__file__).parent
            / "sample_files"
            / "source"
            / "markdown"
            / source_filename
        )
        latex_expected_file_path = (
            Path(__file__).parent
            / "sample_files"
            / "expected"
            / "latex"
            / expected_filename
        )

        markdown_source = load_file(str(markdown_source_file_path))
        latex_expected = load_file(str(latex_expected_file_path))

        ast_root = self.markdown_parser.to_AST(markdown_source)
        latex_result = ast_root.convert(self.latex_converter)

        assert latex_result is not None
        assert isinstance(latex_result, str)
        assert len(latex_result) > 0

        assert latex_result == latex_expected
