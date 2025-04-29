import markup_document_converter.ast as ast
from markup_document_converter.converters.typst_converter import TypstConverter
import pytest  # type: ignore


@pytest.fixture(scope="class")
def typst_converter(request):
    request.cls.typst_converter = TypstConverter()


@pytest.mark.usefixtures("typst_converter")
class TestTypstConverter:
    def test_convert_default(self):
        pass

    def test_convert_document(self):
        document = ast.Document(
            children=[
                ast.Heading(
                    level=1,
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ],
                ),
                ast.Text("Curabitur hendrerit est sed velit molestie maximus"),
                ast.Bold(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus"),
                    ]
                ),
            ]
        )

        result = document.convert(self.typst_converter)

        assert (
            result == "\n"
            "= Curabitur hendrerit est sed velit molestie maximus\n"
            "Curabitur hendrerit est sed velit molestie maximus"
            "*Curabitur hendrerit est sed velit molestie maximus*\n"
        )

    @pytest.mark.parametrize(
        "level,expected",
        [
            (1, "\n= Curabitur hendrerit est sed velit molestie maximus\n"),
            (2, "\n== Curabitur hendrerit est sed velit molestie maximus\n"),
            (3, "\n=== Curabitur hendrerit est sed velit molestie maximus\n"),
            (4, "\n==== Curabitur hendrerit est sed velit molestie maximus\n"),
            (5, "\n===== Curabitur hendrerit est sed velit molestie maximus\n"),
            (6, "\n====== Curabitur hendrerit est sed velit molestie maximus\n"),
        ],
    )
    def test_convert_heading(self, level, expected):
        heading = ast.Heading(
            level=level,
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")],
        )

        result = heading.convert(self.typst_converter)

        assert result == expected

    def test_convert_bold(self):
        bold = ast.Bold(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = bold.convert(self.typst_converter)

        assert result == "*Curabitur hendrerit est sed velit molestie maximus*"

    def test_convert_italic(self):
        italic = ast.Italic(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = italic.convert(self.typst_converter)

        assert result == "_Curabitur hendrerit est sed velit molestie maximus_"

    def test_convert_strike(self):
        strike = ast.Strike(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = strike.convert(self.typst_converter)

        assert result == "#strike[Curabitur hendrerit est sed velit molestie maximus]"

    def test_convert_text(self):
        text = ast.Text("Curabitur hendrerit est sed velit molestie maximus")

        result = text.convert(self.typst_converter)

        assert result == "Curabitur hendrerit est sed velit molestie maximus"

    def test_convert_paragraph(self):
        paragraph = ast.Paragraph(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = paragraph.convert(self.typst_converter)

        assert result == "\nCurabitur hendrerit est sed velit molestie maximus\n"

    def test_convert_line_break(self):
        line_break = ast.LineBreak()

        result = line_break.convert(self.typst_converter)

        assert result == "\\ "

    def test_convert_blockquote(self):
        blockquote = ast.Blockquote(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[Curabitur hendrerit est sed velit molestie maximus]"

    def test_convert_list(self):
        pass

    def test_convert_list_item(self):
        pass

    def test_convert_code_block(self):
        code_block = ast.CodeBlock(language="python", code="print('Hello World!')")

        result = code_block.convert(self.typst_converter)

        assert result == "```python\nprint('Hello World!')\n```"

    def test_convert_inline_code(self):
        inline_code = ast.InlineCode(language="python", code="print('Hello World!')")

        result = inline_code.convert(self.typst_converter)

        assert result == "```python print('Hello World!')```"

    def test_convert_image(self):
        pass

    def test_convert_link(self):
        pass

    def test_convert_horizontal_rule(self):
        pass

    def test_convert_table(self):
        pass

    def test_convert_table_row(self):
        pass

    def test_convert_table_cell(self):
        pass

    def test_convert_task_list_item(self):
        pass
