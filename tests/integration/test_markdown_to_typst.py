from markup_document_converter.converters.typst_converter import TypstConverter
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
def typst_converter(request):
    request.cls.typst_converter = TypstConverter()


@pytest.fixture(scope="class")
def markdown_parser(request):
    request.cls.markdown_parser = MarkdownParser()


@pytest.mark.usefixtures("typst_converter")
@pytest.mark.usefixtures("markdown_parser")
class TestMarkdownToTypst:

    @pytest.mark.parametrize(
        "source_filename, expected_filename",
        [
            ("text_formating.md", "text_formating.typ"),
            ("headings.md", "headings.typ"),
            ("lists.md", "lists.typ"),
            ("links_and_images.md", "links_and_images.typ"),
            ("tables.md", "tables.typ"),
            ("quotes_and_breaks.md", "quotes_and_breaks.typ"),
            ("code_blocks.md", "code_blocks.typ"),
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
        typst_expected_file_path = (
            Path(__file__).parent
            / "sample_files"
            / "expected"
            / "typst"
            / expected_filename
        )

        markdown_source = load_file(str(markdown_source_file_path))
        typst_expected = load_file(str(typst_expected_file_path))

        ast_root = self.markdown_parser.to_AST(markdown_source)
        typst_result = ast_root.convert(self.typst_converter)

        assert typst_result is not None
        assert isinstance(typst_result, str)
        assert len(typst_result) > 0

        assert typst_result == typst_expected
